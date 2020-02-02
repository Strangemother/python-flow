import sys

sys.path.append('./sm')
from machine import engine
from machine.models import Flow
#from machine.main import huey

f = Flow.objects.first()


import dev
dev.main()





from flask import Flask
app = Flask(__name__)

def main():
    app.run(debug=False)

@app.route("/")
def hello():
    return 'hello'


@app.route("/run/<int:flow>/")
def run_flow(flow=None):
    flow_m = Flow.objects.get(pk=flow)
    #v= mm.run_flow(flow_m)
    flow_m.refresh_from_db()
    v=engine.submit(flow_m.pk)
    print(v)
    return v




if __name__ == '__main__':
    main()
