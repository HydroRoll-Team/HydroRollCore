use lib::process_rule_pack;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <rule_pack>", args[0]);
        std::process::exit(1);
    }
    match process_rule_pack(&args[1]) {
        Ok(result) => println!("Result: {}", result),
        Err(e) => eprintln!("Error: {}", e),
    }
}