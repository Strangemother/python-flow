from machine import conf

if conf.patch_conf['patched'] is False:
    print('-- Patching')
    from gevent import monkey; monkey.patch_all()
    from huey import SqliteHuey

    if patch_conf['django'] is not False:
        from machine import django_connect
        django_connect.safe_bind()

    conf.patch_conf['patched'] = True
