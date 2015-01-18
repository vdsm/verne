

from pelican.readers import MarkdownReader

from verne import repository


class VerneMarkdownReader(MarkdownReader):
    def read(self, source_path):
        content, oldmeta = super(VerneMarkdownReader, self).read(source_path)
        assets_path = source_path + '.assets'
        repo = repository.discover()
        assets_key = repo.relpath(assets_path)
        import pdb; pdb.set_trace()
        1

