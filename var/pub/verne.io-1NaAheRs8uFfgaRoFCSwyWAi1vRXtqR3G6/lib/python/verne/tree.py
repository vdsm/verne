import pygit2

"""
High level API for GIT as a general purpose time series database.
All objects immutable by design.
"""

class Tree(object):
    def __init__(self, repo, pygit2_tree):
        if type(pygit2_tree) == pygit2.Oid:
            pygit2_tree = repo.get(pygit2_tree)
        self._tree = pygit2_tree
        self.repo = repo
        self.oid = pygit2_tree.oid

    def __getitem__(self, path):
        entry = self._tree[path]
        if entry.filemode == pygit2.GIT_FILEMODE_BLOB:
            blob = self.repo.get(entry.oid)
            return blob.read_raw()
        elif entry.filemode == pygit2.GIT_FILEMODE_TREE:
            return Tree(self.repo, self.repo.get(entry.oid))
        raise RuntimeError("Unknown filemode %s at %s" %
                (entry.filemode, path))
    
    EMPTY_TREE = object()

    def get_subtree(self, path, default=EMPTY_TREE):
        try:
            entry = self._tree[path]
        except KeyError:
            if default == EMPTY_TREE:
                exists = self.repo.TreeBuilder()
                tree = self.repo.get(exists.write())
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
            
    def insert(self, path, data):
        parts = path.split('/')
        basename = parts.pop()

        # The first builder is the bottom tree that references our given
        # leaf node.
        builder = self._get_tree_builder('/'.join(parts))
        if data == None:
            if builder.get(basename):
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

    def delete(self, path):
        return self.insert(path, None)

    def wrap(self, path):
        """ Bury the tree underneath a new top level path offset """
        if not path:
            raise ValueError("Empty path")
        parts = path.strip('/').rsplit('/', 1)
        builder = self.repo.TreeBuilder()
        builder.insert(parts.pop(), self._tree.oid, pygit2.GIT_FILEMODE_TREE)
        tree_inner = self.repo.get(builder.write())
        tree = Tree(self.repo, tree_inner)
        if parts:
            return tree.wrap(parts.pop())
        return tree
    
    @property
    def hex(self):
        return self._tree.hex

    def __contains__(self, path):
        return path in self._tree

    def _get_tree_builder(self, path):
        oid = None
        if path:
            try:
                oid = self._tree[path].oid
            except KeyError:
                return self.repo.TreeBuilder()
        else:
            oid = self._tree.oid
        return self.repo.TreeBuilder(oid)

    def __iter__(self):
        for entry in iter(self._tree):
            yield entry.name

    def __eq__(self, other):
        return self._tree.oid == other._tree.oid


class Branch(object):
    def __init__(self, repo, branch_name):
        self.ref_name = branch_name
        self.repo = repo
    
    @property
    def exists(self):
        return bool(self.repo.lookup_branch(self.ref_name))
    
    @property
    def head(self):
        ref = self.repo.lookup_branch(self.ref_name)
        return Commit(self.repo, ref.get_object())

    def commit(self, msg, tree):
        ref_to_update = self.ref_name if self.exists else None
        parents = [self.head._commit.oid] if self.exists else []
        author = pygit2.Signature('Alice Author', 'alice@authors.tld')
        committer = pygit2.Signature('Cecil Committer', 'cecil@committers.tld')
        oid = self.repo.create_commit( ref_to_update
                                     , author
                                     , committer
                                     , msg
                                     , tree.oid
                                     , parents
                                     )
        commit = self.repo.get(oid)
        if not ref_to_update:
            self.repo.create_branch(self.ref_name, commit)
        return commit


class Commit(object):
    def __init__(self, repo, commit):
        self.repo = repo
        self._commit = commit
    
    @property
    def tree(self):
        return Tree(self.repo, self._commit.tree)

    @property
    def parents(self):
        return (Commit(self.repo, c) for c in self._commit.parents)

    def recurse(self, trail=()):
        """ Depth first walk of dependencies """
        yield trail, self
        for i, parent in enumerate(self.parents):
            for commit in parent.recurse(trail + (i,)):
                yield commit
