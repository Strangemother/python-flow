
Run the consumer using the bat file. Like this:

    python consumer.py machine.main.huey -k greenlet -w 16

And run the django main interface using the run.bat

    python manage.py runserver

Submit flows through the RPC, import the head.py or main interface:

    from machine import main
    main.submit_flow(55)
