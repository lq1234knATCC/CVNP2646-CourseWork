from network_monitor import parse_packet_line

def test_parse_packet_line():
    line = "1.1.1.1,2.2.2.2,1234,80,TCP,SYN"

    result = parse_packet_line(line)

    assert result["src_ip"] == "1.1.1.1"
    assert result["dst_port"] == 80