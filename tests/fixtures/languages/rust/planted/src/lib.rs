/// Return a greeting for `name`.
pub fn greet(name: &str) -> String {
    format!("Hello, {name}!")
}

#[cfg(test)]
mod tests {
    use super::greet;

    #[test]
    fn greet_names_the_caller() {
        assert_eq!(greet("Ada"), "Hello, Ada");
    }
}
