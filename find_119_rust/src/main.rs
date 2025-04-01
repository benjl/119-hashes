use std::io;
use sha256::digest;
use std::env;
use std::cmp::min;
use std::time::SystemTime;
use std::thread;
use std::sync::mpsc;
use std::fs;

struct BestHash {
    number: usize,
    hash: String,
    count: usize
}

fn fmt_int(n: usize) -> String {
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

fn count_119s(input: &str) -> usize {
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

fn batch_test(start: usize, end: usize, best: usize) -> Vec<BestHash> {
    let mut bests: Vec<BestHash> = Vec::with_capacity(end - start);
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
    batch_test(347000000, 357000000, 3);
    let t2 = SystemTime::now();
    let nps = (357000000.0 - 347000000.0) / t2.duration_since(t1).expect("Clock err").as_secs_f32();
    println!("{} nps", nps);
}

fn load_progress() -> (usize, BestHash) {
    let resume_data = fs::read_to_string(".\\savedprogress.txt").expect("Error reading file.");
    let lines: Vec<&str> = resume_data.split("\n").collect();

    let mut loaded_num: usize = 0;
    let mut loaded_best = BestHash {
        number: 0,
        hash: String::new(),
        count: 0
    };

    for line in lines {
        if line.len() > 1 {
            match &line[..1] {
                "n" => loaded_num = line[1..].parse().unwrap(),
                "b" => loaded_best.count = line[1..].parse().unwrap(),
                "z" => loaded_best.number = line[1..].parse().unwrap(),
                "h" => loaded_best.hash = line[1..].to_string(),
                _ => ()
            }
        }
    }

    return (loaded_num, loaded_best);
}

fn main() {
    const BATCH_SIZE: usize = 5_000_000;
    const WORKERS: usize = 4;

    let mut save_mode = false;

    let mut current_number = 0;
    let mut session_total = 0;
    let mut best = BestHash {
        number: 0,
        hash: String::new(),
        count: 0
    };

    let args: Vec<String> = env::args().collect();
    if args.len() > 1 {
        if args.iter().any(|x| x == "resume") {
            save_mode = true;
            (current_number, best) = load_progress();
            println!("Resuming from {}, Best: [{}] {} -> {}", fmt_int(current_number), best.count, best.number, best.hash);
        }
    }

    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        let stdin = io::stdin();
        loop {
            let mut line = String::new();
            stdin.read_line(&mut line).expect("Failed for some reason");
            let cmd = line.trim_end().to_string();
            tx.send(cmd).unwrap();
        }
    });

    'main_loop: loop {
        let time0 = SystemTime::now();
        let mut threads = Vec::with_capacity(WORKERS);
        for i in 0..WORKERS {
            threads.push(thread::spawn(move || {
                return batch_test(current_number + i * BATCH_SIZE, current_number + (i+1) * BATCH_SIZE, best.count);
            }));
        }

        let mut results: Vec<Vec<BestHash>> = Vec::with_capacity(WORKERS);
        for thr in threads {
            results.push(thr.join().unwrap());
        }

        for result_batch in results {
            for r in result_batch {
                if r.count > best.count {
                    println!("New best: Found [{}] {} -> {}", r.count, r.number, r.hash);
                    best = r;
                } else if r.count > 3 {
                    println!("Found [{}] {} -> {}", r.count, r.number, r.hash);
                }
            }
        }

        current_number += WORKERS * BATCH_SIZE;
        session_total += WORKERS * BATCH_SIZE;

        let time1 = SystemTime::now();
        let nps = (WORKERS * BATCH_SIZE) as f32 / time1.duration_since(time0).expect("Clock err").as_secs_f32();
        println!("{} checked ({} nps)", fmt_int(session_total), fmt_int(nps as usize));

        while let Ok(msg) = rx.try_recv() {
            match msg.to_lowercase().as_str() {
                "quit" => { println!("Quitting..."); break 'main_loop; },
                _ => println!("Unknown command: {msg}")
            }
        }
    }

    println!("Numbers checked this time: {}", fmt_int(session_total));
    println!("Got to {}, best [{}] {} -> {}.", fmt_int(current_number), best.count, best.number, best.hash);
    // let args: Vec<String> = env::args().collect();
    // dbg!(args);
    // let mut input = String::new();
    // io::stdin().read_line(&mut input).expect("Something went wrong.");
    // let number = input.trim();
    // let h = digest(number);
    // let hcount = count_119s(&h);
    // println!("Hash of {}: {}, Count: {}", number, h, hcount);
}
