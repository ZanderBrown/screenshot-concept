pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'kasbah')

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'kasbah.in',
  output: 'kasbah',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

kasbah_sources = [
  '__init__.py',
  'gi_composites.py',
  'main.py',
  'save.py',
  'window.py',
]

install_data(kasbah_sources, install_dir: moduledir)
