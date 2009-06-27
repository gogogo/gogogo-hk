from ragendja.settings_post import settings

settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    'gogogo/jquery-ui-1.7.1.custom.min.js',
    'gogogo/jquery.layout.js',

    # ...
)

settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'gogogo/gogogo.css',
    # ...
)
