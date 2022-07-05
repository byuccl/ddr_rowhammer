using Printf
using LibSerialPort

get_target() = "/dev/ttyUSB1"
get_baudrate() = 115200

open_port() = LibSerialPort.open(get_target(), get_baudrate())

function read_all(io;quiet=false)
    output::String = ""
    while bytesavailable(io) > 0
        result = read(io) |> String
        output *= result
        !quiet && print(result)
        sleep(0.1)
    end
    !quiet && print("\n")
    return output
end

function send_command(io, cmd::String)
    read_all(io)
    println(io, cmd)
    sleep(0.1)
    return read_all(io)
end

function get_memory_size(io)
    output = send_command(io, "mem_list")
    result::RegexMatch = match(r"MAIN_RAM\s+(?'base'0x\d+)\s+(?'size'0x\d+)", output)
    if isnothing(result)
        println("Couldn't find MAIN_RAM info.")
        return nothing
    else
        return (
            base=parse(UInt32, result["base"]),
            size=parse(UInt32, result["size"])
        )
    end
end

function memory_search(io)
    base, size = get_memory_size(io)
    memory_test(io, base, size)
end

function memory_test(io, base, size)
    output = send_command(io, "mem_test $(repr(base)) $(repr(size))")
    if occursin("Memtest KO", output)
        half = size >> 1
        if half > 0
            memory_test(io, base, half)
            memory_test(io, base + half, half)
        end
    end
end