

from pelican.readers import MarkdownReader

from verne import repository


class VerneMarkdownReader(MarkdownReader):
    def read(self, source_path):
        content, oldmeta = super(VerneMarkdownReader, self).read(source_path)
        assets_path = source_path + '.assets'
        repo = repository.discover()
        assets_key = repo.relpath(assets_path)
        try:
            assets = repo.head.tree[assets_key]
        except KeyError:
            meta = oldmeta
        else:
            meta = {}
            for k, v in assets.as_dict().items():
                k = k.lower()
                if k in ('slug', 'title'):
                    v = v.strip()
                meta[k] = self.process_metadata(k, v)
        return content, meta
