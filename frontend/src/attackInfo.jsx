// Short plain-English descriptions of the NSL-KDD attack types, shown in the AI Investigation panel.

export const FAMILY_INFO = {
  DoS: 'Denial of service: the attacker floods or crashes a system so real users cannot use it.',
  Probe: 'Probe: the attacker scans the network to find hosts, open ports and weaknesses before attacking.',
  R2L: 'Remote to local: an attacker with no account on the machine tries to get access to it from the network.',
  U2R: 'User to root: an attacker who already has a normal user account tries to gain administrator (root) access.',

  // CICIDS2017 families
  'Brute force': 'Brute force: the attacker tries many passwords against a login service until one works.',
  'Web attack': 'Web attack: the attacker targets a web application, for example its login page, its forms or its database.',
  Botnet: 'Botnet: infected machines take orders from an attacker\'s control server.',
  Infiltration: 'Infiltration: the attacker gets a foothold inside the network and then explores it from the inside.',
  Exploit: 'Exploit: the attacker abuses a known software flaw to take over or leak data from a system.',
}

export const ATTACK_INFO = {
  // Denial of service
  neptune: 'SYN flood. Sends a stream of TCP connection requests and never finishes the handshake, filling the target\'s connection queue so real users cannot connect.',
  smurf: 'Sends ping requests with the victim\'s address forged as the sender to a whole network, so many machines reply to the victim at once and overwhelm it.',
  back: 'Slows down an Apache web server by sending requests whose address contains a huge number of slashes.',
  pod: '"Ping of death". Sends oversized or malformed ping packets that crash older systems.',
  teardrop: 'Sends overlapping, malformed IP fragments that crash older systems when they try to reassemble the packet.',
  land: 'Sends a packet whose source and destination address and port are identical, which makes some older systems hang.',
  apache2: 'Denial of service against the Apache web server using requests with an enormous number of HTTP headers.',
  mailbomb: 'Floods a mail server or mailbox with a huge number of email messages to use up its resources.',
  processtable: 'Keeps opening connections to a network service until the target\'s process table is full, so it cannot start new processes.',
  udpstorm: 'Sets up a loop between two UDP services (such as echo and chargen) so they keep sending packets to each other and flood the network.',

  // Probe
  ipsweep: 'Pings a whole range of IP addresses to find out which machines are alive.',
  portsweep: 'Tries many ports on a machine to find out which services are listening.',
  nmap: 'Scans hosts and ports with the Nmap tool to map the network and discover which services (and sometimes which operating system) each machine runs.',
  satan: 'Vulnerability scanner (SATAN) that probes machines for known weaknesses.',
  saint: 'Vulnerability scanner (SAINT, a descendant of SATAN) that probes machines for known weaknesses.',
  mscan: 'Multi-host scanning tool. It checks many machines at once for well-known vulnerable services (for example DNS, FTP, mail), so the traffic looks like one source touching many hosts and services.',

  // Remote to local
  guess_passwd: 'Repeatedly guesses passwords for a service to log in as a real user.',
  ftp_write: 'Abuses an FTP server that lets anonymous users write files, to plant files that give the attacker local access.',
  imap: 'Exploits a flaw in an IMAP mail server to run commands on it remotely.',
  multihop: 'Multi-step intrusion: breaks into one machine and then uses it as a stepping stone to attack others.',
  phf: 'Exploits the "phf" script on old web servers to run commands remotely.',
  spy: 'Multi-step intrusion where the attacker gains a foothold and quietly gathers information from the machine.',
  warezclient: 'Downloads illegally copied software ("warez") from a file server the attacker previously set up.',
  warezmaster: 'Abuses write access on an FTP server to upload illegally copied software ("warez") for others to download.',
  named: 'Exploits a flaw in the BIND name server (named) to gain remote access.',
  sendmail: 'Exploits a flaw in the sendmail mail server to run commands remotely.',
  snmpgetattack: 'Sends unauthorized SNMP requests to a network device to read its configuration and status.',
  snmpguess: 'Guesses SNMP community strings (the equivalent of passwords) to get into a network device.',
  worm: 'Self-replicating program that copies itself from machine to machine.',
  xlock: 'Imitates a screen-lock program on an X display to trick a user into typing their password.',
  xsnoop: 'Watches keystrokes on an X display with weak access control to capture passwords and other information.',
  httptunnel: 'Hides other kinds of traffic inside ordinary-looking HTTP, giving the attacker a covert channel that slips past simple filters.',

  // User to root
  buffer_overflow: 'Overflows a program\'s memory buffer so the attacker\'s code runs with higher privileges, usually to get a root shell.',
  loadmodule: 'Exploits a flaw in the loadmodule program to get a root shell.',
  rootkit: 'Installs tools that hide the attacker and keep root access on the machine.',
  perl: 'Exploits a flaw in how Perl runs with elevated privileges to gain root.',
  sqlattack: 'Sends malicious SQL commands to a database to gain higher privileges than the account should have.',
  xterm: 'Exploits a buffer overflow in the xterm program to gain root.',
  ps: 'Exploits a flaw in the ps (process status) program to gain root.',

  // CICIDS2017 (names are lower case here because describeAlert lower-cases the label)
  'dos hulk': 'HULK web flood. Sends a stream of unique, generated web requests so the server cannot answer them from its cache and runs out of capacity.',
  'ddos': 'Distributed denial of service. Many machines flood the target at once so real users cannot get through (in this dataset it was generated with the LOIC tool).',
  'dos goldeneye': 'GoldenEye web flood. Sends random web requests over connections it keeps open, to exhaust the web server.',
  'dos slowloris': 'Slowloris. Opens many connections and sends each request very slowly, so the server\'s connection slots stay full.',
  'dos slowhttptest': 'Slow HTTP attack. Sends headers, request bodies or reads responses extremely slowly to tie up the web server.',
  'portscan': 'Tries many ports on a machine, with different scan types, to find out which services are listening.',
  'ftp-patator': 'Uses the Patator tool to guess FTP passwords until a login works.',
  'ssh-patator': 'Uses the Patator tool to guess SSH passwords until a login works.',
  'web attack - brute force': 'Repeatedly guesses the username and password on a web application\'s login page.',
  'web attack - xss': 'Cross-site scripting. Injects a malicious script into a web page so it runs in other visitors\' browsers.',
  'web attack - sql injection': 'Sends specially crafted SQL through a web form or address to read or change the database behind it.',
  'bot': 'A botnet. An infected machine checks in with the attacker\'s control server and carries out its commands.',
  'infiltration': 'The attacker gets a foothold on an internal machine (in this dataset through a malicious file) and then probes the network from inside.',
  'heartbleed': 'Exploits the OpenSSL Heartbleed bug to read secrets such as keys and passwords from a server\'s memory.',
}

export function describeAlert(label) {
  const key = String(label).trim().toLowerCase()
  if (key === 'normal' || key === 'benign') {
    return 'The dataset labels this record as normal traffic, so this alert is a false alarm.'
  }
  return ATTACK_INFO[key] ?? 'No description is available for this attack type.'
}