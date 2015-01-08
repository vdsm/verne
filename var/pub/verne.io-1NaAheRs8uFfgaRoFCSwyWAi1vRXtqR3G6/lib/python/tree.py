import pygit2


class Commit(object):
    def __init__(self, repo, pygit2_commit):
        self._commit = pygit2_commit
        self.oid = pygit2_commit.oid
        self.repo = repo

    @property
    def tree(self):
        return Tree(self.repo, self._commit.tree)

    def log(self):
        log_ = self.repo.walk(self._commit.oid, pygit2.GIT_SORT_TIME)
        return (Commit(self.repo, c) for c in log_)

    def branch(self, name, force=False):
        branch = self.repo.create_branch(name, self._commit, force)
        return Branch(self.repo, branch.name)


class Tree(object):
    def __init__(self, repo, pygit2_tree):
        self._tree = pygit2_tree
        self.repo = repo
        self.oid = pygit2_tree.oid


    def __getitem__(self, path):
        if entry.filemode == pygit2.GIT_FILEMODE_BLOB:
            blob = self.repo.get(entry.id)
            return blob.read_raw()
        elif entry.filemode == pygit2.GIT_FILEMODE_TREE:
            return Tree(self.repo, self.repo.get(entry.id))
        raise RuntimeError("Unknown filemode %s at %s" %
                (entry.filemode, path))
    
    EMPTY_TREE = object()

    def get_subtree(self, path, default=EMPTY_TREE):
        try:
            entry = self._tree[path]
        except KeyError:
            if default == EMPTY_TREE:
                empty = self.repo.TreeBuilder()
                tree = self.repo.get(empty.write())
                return Tree(self.repo, tree)
            raise
        if entry.filemode == pygit2.GIT_FILEMODE_TREE:
            tree = self.repo.get(entry.id)
            return Tree(self.repo, tree)
        else:
            raise NotASubtree(path)

    def get_blob(self, path, default=""):
        try:
            entry = self._tree[path]
        except KeyError:
            return default
        if entry.filemode == pygit2.GIT_FILEMODE_BLOB:
            return self.repo.get(entry.id).read_raw()
        else:
            raise NotABlob(path)
            
    def set(self, path, data):
        parts = path.split('/')
        basename = parts.pop()

        # The first builder is the bottom tree that references our given
        # leaf node.
        builder = self._get_tree_builder('/'.join(parts))
        if data == None:
            builder.remove(basename)
        else:
            blob_id = self.repo.create_blob(data)
            builder.insert(basename, blob_id, pygit2.GIT_FILEMODE_BLOB)

        # Now we replace all the parent trees to point to our new tree
        # until we hit the root.
        while parts:
            name = parts.pop()
            child_oid = builder.write()
            builder = self._get_tree_builder('/'.join(parts))
            builder.insert(name, child_oid, pygit2.GIT_FILEMODE_TREE)

        tree = self.repo.get(builder.write())
        return Tree(self.repo, tree)

    def wrap(self, path):
        """ Bury the tree underneath a new top level path offset """
        if not path:
            raise ValueError("Empty path")
        parts = path.strip('/').rsplit('/', 2)
        builder = self.repo.TreeBuilder()
        builder.insert(parts.pop(), self._tree, pygit2.GIT_FILEMODE_TREE)
        tree_inner = self.repo.get(builder.write())
        tree = Tree(self.repo, tree_inner)
        if parts:
            return tree.wrap(parts.pop())
        return tree

    def __contains__(self, path):
        return path in self._tree

    def _get_tree_builder(self, path):
        oid = None
        if path:
            if path in self._tree:
                oid = self._tree[path].oid
            else:
                return self.repo.TreeBuilder()
        else:
            oid = self._tree.oid
        return self.repo.TreeBuilder(oid)

    def __iter__(self):
        return iter(self._tree)

    def __eq__(self, other):
        return self._tree.oid == other._tree.oid


def flatten_tree(tree, prefix=()):
    """ Flatten a tree into name -> entry pairs """
    for entry in tree._tree:
        name = prefix + (entry.name,)
        if entry.filemode == pygit2.GIT_FILEMODE_TREE:
            subtree = tree.subtree(entry.name)
            for item in flatten_tree(subtree, name):
                yield item
        else:
            yield (name, entry)


class Branch(object):
    """ Mutable branch object """
    alice = pygit2.Signature('Alice Author', 'alice@authors.tld')
    cecil = pygit2.Signature('Cecil Committer', 'cecil@committers.tld')

    def __init__(self, repo, branch_name):
        self.ref_name = branch_name
        self.repo = repo
        _tree = repo.lookup_reference(self.ref_name).peel().tree
        self.tree = Tree(repo, _tree)

    @classmethod
    def discover(cls):
        repodir = pygit2.discover_repository('.')
        repo = pygit2.Repository(repodir)
        return cls(repo, repo.head.name)

    def __contains__(self, path):
        return path in self.tree

    def __getitem__(self, name):
        return self.tree[name]

    def __setitem__(self, path, value):
        self.tree = self.tree.set(path, value)

    def __delitem__(self, path):
        self[path] = None

    def commit(self, msg, author=alice, committer=cecil):
        ref = self.repo.lookup_reference(self.ref_name)
        parent = ref.peel().id
        self.repo.create_commit( self.ref_name
                               , author
                               , committer
                               , msg
                               , self.tree._tree.oid
                               , [parent]
                               )
