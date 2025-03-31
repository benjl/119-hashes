use std::io;
use sha256::digest;


fn main() {
    let input = "834152113309";
    let h = digest(input);
    println!("Hash: {}", h);
}
