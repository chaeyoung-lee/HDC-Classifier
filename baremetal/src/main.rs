#![no_std]
#![no_main]

use panic_halt as _;

use cortex_m_rt::entry;
use cortex_m::peripheral::Peripherals;
use embassy_stm32::gpio::{Level, Output, Speed};
use embassy_time::Timer;

#[entry]
fn main() -> ! {
    let p = embassy_stm32::init(Default::default());
}