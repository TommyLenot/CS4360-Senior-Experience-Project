COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land",
    "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", "num_compromised",
    "root_shell", "su_attempted", "num_root", "num_file_creations", "num_shells",
    "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count",
    "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
    "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate", "dst_host_srv_rerror_rate",
    "label", "difficulty",
]

FEATURES = COLUMNS[:-2]  # everything except label and difficulty

# NSL-KDD attack label -> attack family
FAMILIES = {
    "DoS": ["back", "land", "neptune", "pod", "smurf", "teardrop", "apache2",
            "mailbomb", "processtable", "udpstorm"],
    "Probe": ["ipsweep", "nmap", "portsweep", "satan", "mscan", "saint"],
    "R2L": ["ftp_write", "guess_passwd", "imap", "multihop", "phf", "spy",
            "warezclient", "warezmaster", "named", "sendmail", "snmpgetattack",
            "snmpguess", "worm", "xlock", "xsnoop", "httptunnel"],
    "U2R": ["buffer_overflow", "loadmodule", "perl", "rootkit", "ps",
            "sqlattack", "xterm"],
}
_LABEL_TO_FAMILY = {label: fam for fam, labels in FAMILIES.items() for label in labels}


def family(label):
    """Map an NSL-KDD label (e.g. 'neptune') to normal/DoS/Probe/R2L/U2R/unknown."""
    label = str(label).strip().lower().rstrip(".")
    if label == "normal":
        return "normal"
    return _LABEL_TO_FAMILY.get(label, "unknown")
