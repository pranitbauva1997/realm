pub fn magic(req: realm::Request) -> realm::Result {
    let input = realm::request_config::RequestConfig::new(req)?;
    match input.path.as_str() {
        "/" => crate::routes::index::layout(&input.req),
        url_ => crate::cms::layout(&input.req, crate::cms::get_context("cms"), url_),
    }
}