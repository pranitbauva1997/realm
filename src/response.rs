use hyper;

pub struct Response {
    // title: Maybe<String>,
    new_path: String,
    // external_redirect:
    replace: bool,
    // headers:
    // cookies
    // status code
    // x-sendfile

    // seo stuff

    // id
    // config
}

impl Response {
    // pub fn empty() -> Response {}
    // pub fn add_cookie(key: String, value: String) {}
    // pub fn new(id: String, config: String) -> Response {}
    // pub fn api(json) -> Response {}

    pub fn to_hyper(self) -> hyper::Response<hyper::Body> {
        unimplemented!()
    }
}