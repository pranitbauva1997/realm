port module Realm.Ports exposing (..)

import Json.Encode as JE


port submit : JE.Value -> Cmd msg


port navigate : String -> Cmd msg


port shutdown : (() -> msg) -> Sub msg


port toIframe : JE.Value -> Cmd msg


port fromIframe : (JE.Value -> msg) -> Sub msg


port changePage : JE.Value -> Cmd msg


port viewPortChanged : (JE.Value -> msg) -> Sub msg


port onUnloading : (Bool -> msg) -> Sub msg


port setLoading : () -> Cmd msg


port cancelLoading : () -> Cmd msg


port disableScrolling : () -> Cmd msg


port enableScrolling : () -> Cmd msg
