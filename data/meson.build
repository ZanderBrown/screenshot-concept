desktop_file = i18n.merge_file(
  input: 'org.gnome.Kasbah.desktop.in',
  output: 'org.gnome.Kasbah.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'org.gnome.Kasbah.appdata.xml.in',
  output: 'org.gnome.Kasbah.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

configure_file(input: 'org.gnome.Kasbah.service.in',
               output: 'org.gnome.Kasbah.service',
               configuration: conf,
               install_dir: join_paths([get_option('datadir'),'dbus-1/services']))

install_data('org.gnome.Kasbah.svg',
             install_dir: join_paths([get_option('datadir'),'icons/hicolor/scalable/apps']))

install_data('org.gnome.Kasbah.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif
