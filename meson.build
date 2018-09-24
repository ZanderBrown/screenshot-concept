project('kasbah',         version: '0.1.0',
  meson_version: '>= 0.40.0',
)

i18n = import('i18n')

bindir = join_paths([ get_option('prefix'), 'bin' ])

conf = configuration_data()
conf.set('BINDIR', bindir)

subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
