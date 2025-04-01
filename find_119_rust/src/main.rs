use std::io;
use sha256::digest;
use std::env;
use std::cmp::min;
use std::time::SystemTime;
use std::thread;

struct BestHash {
    number: u64,
    hash: String,
    count: u64
}

fn fmt_int(n: u64) -> String {
    if n >= 1000000000000 {
        return format!("{}T", (n as f64 / 10000000000.0).round() / 100.0);
    } else if n >= 1000000000 {
        return format!("{}B", (n as f64 / 10000000.0).round() / 100.0);
    } else if n >= 1000000 {
        return format!("{}M", (n as f64 / 10000.0).round() / 100.0);
    } else if n >= 10000 {
        return format!("{}K", (n as f64 / 10.0).round() / 100.0);
    } else {
        return format!("{}", n);
    }
}

fn count_119s(input: &str) -> u64 {
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

fn batch_test(start: u64, end: u64, best: u64) -> Vec<BestHash> {
    let mut bests: Vec<BestHash> = Vec::new();
    for n in start..end {
        let h = digest(n.to_string());
        let c = count_119s(&h);
        if c > min(3, best) {
            bests.push(BestHash { number: n, hash: h, count: c });
        }
    }
    return bests;
}

fn benchmark() {
    let t1 = SystemTime::now();
    let results = batch_test(347000000, 357000000, 3);
    let t2 = SystemTime::now();
    let nps = (357000000.0 - 347000000.0) / t2.duration_since(t1).expect("Clock err").as_secs_f32();
    println!("{} nps", nps);
}

fn main() {

    // let args: Vec<String> = env::args().collect();
    // dbg!(args);
    // let mut input = String::new();
    // io::stdin().read_line(&mut input).expect("Something went wrong.");
    // let number = input.trim();
    // let h = digest(number);
    // let hcount = count_119s(&h);
    // println!("Hash of {}: {}, Count: {}", number, h, hcount);

    benchmark();
}
