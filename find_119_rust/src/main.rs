use std::io;
use sha256::digest;

fn count_119s(input: &str) -> u32 {
    let mut count = 0;
    let mut state = 0;
    for c in input.chars() {
        match state {
            0 => match c {
                '1' => state = 1,
                _ => state = 0,
            },
            1 => match c {
                '1' => state = 2,
                _ => state = 0,
            },
            2 => match c {
                '1' => (),
                '9' => { state = 0; count = count + 1; },
                _ => state = 0,
            },
            _ => state = 0,
        }
    }
    return count;
}

fn main() {
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("Soimething went wrong.");
    let number = input.trim();
    let h = digest(number);
    let hcount = count_119s(&h);
    println!("Hash of {}: {}, Count: {}", number, h, hcount);
}
