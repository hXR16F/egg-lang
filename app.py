import egglang
from json import dumps

from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="memory://",
)

limit_encode = 500
limit_decode = limit_encode * 12
limit_decode_eggs = limit_decode // 4

def go_home(type_of_redirect: str):
    if type_of_redirect == "render":
        return render_template("index.html", limit_encode=limit_encode, limit_decode=limit_decode, limit_decode_eggs=limit_decode_eggs)
    elif type_of_redirect == "redirect":
        return redirect("/egg-lang/")

def jsonify(status=200, indent=4, sort_keys=False, **kwargs):
    response = make_response(dumps(dict(**kwargs), ensure_ascii=False, indent=indent, sort_keys=sort_keys))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["mimetype"] = "application/json"
    response.status_code = status
    return response

def api_error(return_type: str):
    if return_type == "raw":
        return "Error"
    elif return_type == "json":
        return jsonify(success=False)

@app.route("/")
@limiter.limit("4/second")
def index():
    # here will be probably some other stuff
    return redirect("/egg-lang/")

@app.route("/egg-lang/")
@limiter.limit("4/second")
def egg_lang():
    return go_home("render")

@app.route("/egg-lang/<string:encode_or_decode>", methods=["POST"])
@limiter.limit("2/second")
def encoder_decoder(encode_or_decode, *args):
    if encode_or_decode != "encode" and encode_or_decode != "decode":
        if args == ():
            return go_home("redirect")
        else:
            return api_error(args[0])

    if encode_or_decode == "encode":
        limit = limit_encode
    elif encode_or_decode == "decode":
        limit = limit_decode

    try:
        text = request.form.get("text")
        length = len(text)
    except:
        if args == ():
            return go_home("redirect")
        else:
            return api_error(args[0])

    if length > limit:
        exceeded_limit = True
        encoded_decoded = None
    else:
        exceeded_limit = False
        try:
            if encode_or_decode == "encode":
                encoded_decoded, is_error = egglang.encode(text)
            elif encode_or_decode == "decode":
                encoded_decoded, is_error = egglang.decode(text)
        except:
            pass

    if args == ():
        if length == 0:
            return go_home("redirect")
        if not encoded_decoded:
            if not exceeded_limit:
                return go_home("redirect")
            
            if encode_or_decode == "encode":
                return render_template("generate.html", converted=f"Exceeded encoding limit ({length}/{limit} chars)", placeholder=True)
            elif encode_or_decode == "decode":
                return render_template("generate.html", converted=f"Exceeded decoding limit ({length}/{limit} chars)", placeholder=True)

        if is_error:
            if encode_or_decode == "encode":
                return render_template("generate.html", converted="Error while encoding", placeholder=True)
            elif encode_or_decode == "decode":
                return render_template("generate.html", converted="Error while decoding", placeholder=True)

        return render_template("generate.html", converted=encoded_decoded)
    else:
        if length == 0 or not encoded_decoded or is_error:
            return api_error(args[0])

        if args[0] == "raw":
            return encoded_decoded
        elif args[0] == "json":
            return jsonify(success=True, text=encoded_decoded)

@app.route("/api/egg-lang/<string:encode_or_decode>/<string:return_type>", methods=["POST"])
@limiter.limit("20/minute")
def api_encode_decode(encode_or_decode, return_type):
    if encode_or_decode != "encode" and encode_or_decode != "decode":
        if return_type == "json":
            return api_error("json")

        return api_error("raw")

    if return_type == "json":
        return encoder_decoder(encode_or_decode, "json")
    elif return_type == "raw":
        return encoder_decoder(encode_or_decode, "raw")
    else:
        return api_error("raw")

if __name__ == "__main__":
    from waitress import serve
    # serve(app, host="0.0.0.0", port=20583) # ipv4
    serve(app, host="::", port=20583) # ipv6

    # app.run(debug=True)