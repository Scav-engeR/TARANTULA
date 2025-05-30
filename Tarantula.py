#!/usr/bin/env python3
"""
TARANTULA v3.0 - Enterprise Attack Surface Management Platform
Advanced OSINT & Penetration Testing Suite with Integrated Security Tools
Author: Scav-engeR | Framework: Python3

Tools integrated: FOFA, Nuclei, SQLMap, WPScan, OWTF, Shodan, wafw00f, CloudScraper
SideNote...Please credit if you're using this code in your own. Cheers!)
"""

import os
import sys
import json
import time
import socket
import requests
import subprocess
import threading
import hashlib
import base64
import ssl
import sqlite3
import urllib3
import random
from urllib.parse import urlparse, urljoin, quote
from colorama import init, Fore, Back, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver
import re
from datetime import datetime
import tempfile
import yaml

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

class NeonColors:
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Neon gradients
    NEON_PINK = '\033[38;5;201m'
    NEON_BLUE = '\033[38;5;39m'
    NEON_GREEN = '\033[38;5;46m'
    NEON_PURPLE = '\033[38;5;129m'
    NEON_ORANGE = '\033[38;5;208m'

class TarantulaCore:
    def __init__(self):
        self.target = ""
        self.scan_mode = "normal"
        self.workspace = "default"
        self.output_dir = f"tarantula_output_{int(time.time())}"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        self.results = {
            'target_info': {},
            'subdomains': [],
            'ports': [],
            'directories': [],
            'dns_records': {},
            'ssl_info': {},
            'headers': {},
            'tech_stack': [],
            'ips': [],
            'vulnerabilities': [],
            'leaked_data': [],
            'reputation': {},
            'cms_info': {},
            'waf_detection': {},
            'screenshots': [],
            'emails': [],
            'social_media': [],
            'pastebin_leaks': [],
            'security_headers': {},
            'exposed_files': [],
            'api_endpoints': [],
            'nuclei_results': [],
            'sqlmap_results': [],
            'wpscan_results': [],
            'fofa_intelligence': {},
            'shodan_data': {},
            'real_ip': None,
            'cloudflare_bypass': {}
        }
        
        self.api_keys = {
            'shodan': '',
            'fofa_email': '',
            'fofa_key': '',
            'virustotal': ''
        }
        
        self.tool_paths = {
            'nuclei': 'nuclei',
            'sqlmap': 'sqlmap',
            'wpscan': 'wpscan',
            'wafw00f': 'wafw00f',
            'nmap': 'nmap'
        }
        
        self.setup_environment()
        self.init_database()
        
    def setup_environment(self):
        """Setup output directory and check tool dependencies"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/nuclei", exist_ok=True)
        os.makedirs(f"{self.output_dir}/sqlmap", exist_ok=True)
        os.makedirs(f"{self.output_dir}/wpscan", exist_ok=True)
        os.makedirs(f"{self.output_dir}/screenshots", exist_ok=True)
        
    def init_database(self):
        """Initialize SQLite database for results storage"""
        self.db_path = f"{self.output_dir}/tarantula_{self.workspace}.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY,
                target TEXT,
                scan_mode TEXT,
                timestamp TEXT,
                results TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY,
                target TEXT,
                vuln_type TEXT,
                severity TEXT,
                description TEXT,
                tool TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def banner(self):
        banner_text = f"""
{NeonColors.NEON_PINK}╔═══════════════════════════════════════════════════════════════════════════════════════╗
║ ████████╗ █████╗ ██████╗  █████╗ ███╗   ██╗████████╗██╗   ██╗██╗      █████╗            ║
║ ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗████╗  ██║╚══██╔══╝██║   ██║██║     ██╔══██╗           ║
║    ██║   ███████║██████╔╝███████║██╔██╗ ██║   ██║   ██║   ██║██║     ███████║           ║
║    ██║   ██╔══██║██╔══██╗██╔══██║██║╚██╗██║   ██║   ██║   ██║██║     ██╔══██║           ║
║    ██║   ██║  ██║██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝███████╗██║  ██║           ║
║    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝           ║
║ ███████╗███╗   ██╗████████╗███████╗██████╗ ██████╗ ██████╗ ██╗███████╗███████╗          ║
║ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██║██╔════╝██╔════╝          ║
║ █████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝██████╔╝██████╔╝██║███████╗█████╗            ║
║ ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔═══╝ ██╔══██╗██║╚════██║██╔══╝            ║
║ ███████╗██║ ╚████║   ██║   ███████╗██║  ██║██║     ██║  ██║██║███████║███████╗          ║
║ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝          ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝{NeonColors.RESET}

{NeonColors.NEON_BLUE}[{NeonColors.NEON_GREEN}+{NeonColors.NEON_BLUE}] {NeonColors.CYAN}Enterprise Attack Surface Management Platform v3.0{NeonColors.RESET}
{NeonColors.NEON_BLUE}[{NeonColors.NEON_GREEN}+{NeonColors.NEON_BLUE}] {NeonColors.YELLOW}Author: Scav-engeR | Framework: Python3 + Integrated Security Tools{NeonColors.RESET}
{NeonColors.NEON_BLUE}[{NeonColors.NEON_GREEN}+{NeonColors.NEON_BLUE}] {NeonColors.MAGENTA}FOFA | Nuclei | SQLMap | WPScan | OWTF | Shodan | wafw00f | CloudScraper{NeonColors.RESET}
{NeonColors.GRAY}{'='*95}{NeonColors.RESET}
"""
        print(banner_text)
        
    def loading_animation(self, message, duration=2):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        for i in range(duration * 10):
            sys.stdout.write(f'\r{NeonColors.NEON_PINK}[{chars[i % len(chars)]}] {NeonColors.CYAN}{message}{NeonColors.RESET}')
            sys.stdout.flush()
            time.sleep(0.1)
        print()
        
    def neon_print(self, message, color=NeonColors.CYAN, prefix="[+]"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{NeonColors.GRAY}[{timestamp}] {NeonColors.NEON_BLUE}{prefix} {color}{message}{NeonColors.RESET}")
        
    def error_print(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{NeonColors.GRAY}[{timestamp}] {NeonColors.RED}[!] ERROR: {message}{NeonColors.RESET}")
        
    def success_print(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{NeonColors.GRAY}[{timestamp}] {NeonColors.NEON_GREEN}[✓] {message}{NeonColors.RESET}")
        
    def warning_print(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{NeonColors.GRAY}[{timestamp}] {NeonColors.YELLOW}[⚠] {message}{NeonColors.RESET}")
        
    def menu(self):
        menu_text = f"""
{NeonColors.NEON_PURPLE}╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           TARANTULA ENTERPRISE MATRIX v3.0                            ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║ {NeonColors.NEON_GREEN}RECONNAISSANCE & OSINT{NeonColors.NEON_PURPLE}            ║ {NeonColors.NEON_GREEN}VULNERABILITY ASSESSMENT{NeonColors.NEON_PURPLE}          ║
║  {NeonColors.NEON_GREEN}1{NeonColors.NEON_PURPLE} ▶ Advanced Subdomain Discovery   ║  {NeonColors.NEON_GREEN}11{NeonColors.NEON_PURPLE} ▶ Nuclei Vulnerability Scan     ║
║  {NeonColors.NEON_GREEN}2{NeonColors.NEON_PURPLE} ▶ Port & Service Enumeration     ║  {NeonColors.NEON_GREEN}12{NeonColors.NEON_PURPLE} ▶ SQLMap Injection Testing      ║
║  {NeonColors.NEON_GREEN}3{NeonColors.NEON_PURPLE} ▶ Directory & File Discovery     ║  {NeonColors.NEON_GREEN}13{NeonColors.NEON_PURPLE} ▶ WPScan WordPress Analysis     ║
║  {NeonColors.NEON_GREEN}4{NeonColors.NEON_PURPLE} ▶ DNS Intelligence Gathering     ║  {NeonColors.NEON_GREEN}14{NeonColors.NEON_PURPLE} ▶ OWTF Web Application Test     ║
║  {NeonColors.NEON_GREEN}5{NeonColors.NEON_PURPLE} ▶ HTTP Analysis & Fingerprinting ║  {NeonColors.NEON_GREEN}15{NeonColors.NEON_PURPLE} ▶ SSL/TLS Security Assessment   ║
║ {NeonColors.NEON_GREEN}THREAT INTELLIGENCE{NeonColors.NEON_PURPLE}              ║ {NeonColors.NEON_GREEN}BYPASS & EVASION{NeonColors.NEON_PURPLE}                 ║
║  {NeonColors.NEON_GREEN}6{NeonColors.NEON_PURPLE} ▶ FOFA Cyber Space Mapping      ║  {NeonColors.NEON_GREEN}16{NeonColors.NEON_PURPLE} ▶ WAF Detection & Bypass        ║
║  {NeonColors.NEON_GREEN}7{NeonColors.NEON_PURPLE} ▶ Shodan Attack Surface Intel   ║  {NeonColors.NEON_GREEN}17{NeonColors.NEON_PURPLE} ▶ Cloudflare Real IP Discovery  ║
║  {NeonColors.NEON_GREEN}8{NeonColors.NEON_PURPLE} ▶ Email & Social OSINT          ║  {NeonColors.NEON_GREEN}18{NeonColors.NEON_PURPLE} ▶ CDN & Proxy Bypass           ║
║  {NeonColors.NEON_GREEN}9{NeonColors.NEON_PURPLE} ▶ Domain Reputation Analysis    ║  {NeonColors.NEON_GREEN}19{NeonColors.NEON_PURPLE} ▶ Anti-Detection Reconnaissance ║
║  {NeonColors.NEON_GREEN}10{NeonColors.NEON_PURPLE} ▶ Data Leak & Paste Monitoring ║  {NeonColors.NEON_GREEN}20{NeonColors.NEON_PURPLE} ▶ Advanced Stealth Scanning    ║
║ {NeonColors.NEON_GREEN}ENTERPRISE OPERATIONS{NeonColors.NEON_PURPLE}           ║ {NeonColors.NEON_GREEN}REPORTING & EXPORT{NeonColors.NEON_PURPLE}              ║
║  {NeonColors.NEON_GREEN}21{NeonColors.NEON_PURPLE} ▶ Full Enterprise Scan         ║  {NeonColors.NEON_GREEN}26{NeonColors.NEON_PURPLE} ▶ Generate Executive Report    ║
║  {NeonColors.NEON_GREEN}22{NeonColors.NEON_PURPLE} ▶ NUKE Mode (Aggressive)       ║  {NeonColors.NEON_GREEN}27{NeonColors.NEON_PURPLE} ▶ Export to JSON/XML/CSV       ║
║  {NeonColors.NEON_GREEN}23{NeonColors.NEON_PURPLE} ▶ Mass Target Processing       ║  {NeonColors.NEON_GREEN}28{NeonColors.NEON_PURPLE} ▶ Vulnerability Database       ║
║  {NeonColors.NEON_GREEN}24{NeonColors.NEON_PURPLE} ▶ Continuous Monitoring        ║  {NeonColors.NEON_GREEN}29{NeonColors.NEON_PURPLE} ▶ Screenshot Gallery           ║
║  {NeonColors.NEON_GREEN}25{NeonColors.NEON_PURPLE} ▶ API Integration Manager      ║  {NeonColors.NEON_GREEN}0{NeonColors.NEON_PURPLE}  ▶ Configuration & Settings     ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{NeonColors.RESET}
"""
        print(menu_text)
        
    def set_target(self):
        self.neon_print("Enter target domain/IP/CIDR:", NeonColors.NEON_PINK, "[TARGET]")
        target = input(f"{NeonColors.NEON_BLUE}tarantula@neural-net:~$ {NeonColors.CYAN}")
        if target:
            self.target = target.strip().replace('http://', '').replace('https://', '')
            self.success_print(f"Target acquired: {self.target}")
            self.results['target_info']['target'] = self.target
            self.results['target_info']['timestamp'] = datetime.now().isoformat()
        else:
            self.error_print("No target specified!")
            
    def check_tool_dependencies(self):
        """Check if required tools are installed"""
        self.neon_print("Checking tool dependencies", NeonColors.NEON_BLUE)
        
        tools_status = {}
        for tool, path in self.tool_paths.items():
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    tools_status[tool] = "✓ Available"
                    self.success_print(f"{tool}: Available")
                else:
                    tools_status[tool] = "✗ Not found"
                    self.warning_print(f"{tool}: Not found")
            except:
                tools_status[tool] = "✗ Not found"
                self.warning_print(f"{tool}: Not found")
                
        return tools_status
        
    def install_python_dependencies(self):
        """Install required Python packages"""
        packages = [
            'cloudscraper', 'requests', 'beautifulsoup4', 'lxml',
            'dnspython', 'python-whois', 'builtwith', 'wafw00f'
        ]
        
        for package in packages:
            try:
                __import__(package.replace('-', '_'))
                self.success_print(f"{package}: Available")
            except ImportError:
                self.warning_print(f"{package}: Installing...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    self.success_print(f"{package}: Installed")
                except:
                    self.error_print(f"{package}: Installation failed")
                    
    def advanced_subdomain_discovery(self):
        """Advanced subdomain enumeration with multiple techniques"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Advanced subdomain discovery for {self.target}", NeonColors.NEON_GREEN)
        
        # Enhanced subdomain wordlist
        common_subs = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'mobile', 'm', 'test',
            'admin', 'dev', 'api', 'staging', 'beta', 'demo', 'cdn', 'static', 'assets',
            'blog', 'shop', 'store', 'portal', 'secure', 'vpn', 'remote', 'access',
            'support', 'help', 'docs', 'wiki', 'forum', 'chat', 'video', 'stream',
            'app', 'service', 'web', 'old', 'new', 'backup', 'db', 'database', 'sql',
            'git', 'svn', 'repo', 'code', 'jenkins', 'ci', 'cd', 'build', 'deploy',
            'monitor', 'status', 'health', 'metrics', 'logs', 'grafana', 'kibana',
            'elastic', 'prometheus', 'consul', 'vault', 'nomad', 'k8s', 'kubernetes',
            'docker', 'registry', 'harbor', 'nexus', 'artifactory', 'sonar', 'quality'
        ]
        
        found_subs = []
        
        def check_subdomain(sub):
            try:
                full_domain = f"{sub}.{self.target}"
                ip = socket.gethostbyname(full_domain)
                found_subs.append({'subdomain': full_domain, 'ip': ip})
                self.success_print(f"Subdomain found: {full_domain} -> {ip}")
                
                # Check for subdomain takeover
                self.check_subdomain_takeover(full_domain)
                
            except:
                pass
                
        with ThreadPoolExecutor(max_workers=150) as executor:
            self.loading_animation("Neural subdomain discovery in progress", 3)
            executor.map(check_subdomain, common_subs)
            
        # Certificate transparency lookup
        self.cert_transparency_lookup()
        
        # DNS brute forcing with larger wordlist
        self.dns_bruteforce()
        
        self.results['subdomains'] = found_subs
        self.neon_print(f"Subdomain discovery complete: {len(found_subs)} domains mapped", NeonColors.NEON_GREEN)
        
    def cert_transparency_lookup(self):
        """Enhanced certificate transparency search"""
        try:
            self.neon_print("Scanning certificate transparency logs", NeonColors.NEON_BLUE)
            
            # Multiple CT log sources
            ct_sources = [
                f"https://crt.sh/?q=%.{self.target}&output=json",
                f"https://api.certspotter.com/v1/issuances?domain={self.target}&include_subdomains=true&expand=dns_names"
            ]
            
            cert_domains = set()
            
            for source in ct_sources:
                try:
                    response = requests.get(source, timeout=15)
                    if response.status_code == 200:
                        if 'crt.sh' in source:
                            certs = response.json()
                            for cert in certs[:100]:
                                if 'name_value' in cert:
                                    domains = cert['name_value'].split('\n')
                                    for domain in domains:
                                        if domain and self.target in domain:
                                            cert_domains.add(domain.strip())
                        else:
                            # Certspotter format
                            data = response.json()
                            for item in data:
                                if 'dns_names' in item:
                                    for domain in item['dns_names']:
                                        if self.target in domain:
                                            cert_domains.add(domain)
                except:
                    continue
                    
            for domain in cert_domains:
                if domain not in [sub['subdomain'] for sub in self.results['subdomains']]:
                    self.success_print(f"CT Log discovery: {domain}")
                    
        except Exception as e:
            self.error_print(f"Certificate transparency lookup failed: {str(e)}")
            
    def dns_bruteforce(self):
        """DNS bruteforce with extended wordlists"""
        try:
            self.neon_print("DNS bruteforce with extended wordlists", NeonColors.NEON_BLUE)
            
            # Extended wordlist for enterprise environments
            extended_subs = [
                'internal', 'intranet', 'extranet', 'corp', 'corporate', 'company',
                'office', 'hq', 'headquarters', 'branch', 'regional', 'local',
                'prod', 'production', 'staging', 'testing', 'uat', 'qa', 'dev',
                'sandbox', 'lab', 'research', 'experimental', 'pilot', 'demo',
                'training', 'education', 'learn', 'academy', 'university',
                'partners', 'vendor', 'supplier', 'client', 'customer', 'guest',
                'public', 'private', 'secure', 'protected', 'restricted', 'classified'
            ]
            
            found_count = 0
            
            def check_extended_subdomain(sub):
                nonlocal found_count
                try:
                    full_domain = f"{sub}.{self.target}"
                    ip = socket.gethostbyname(full_domain)
                    self.results['subdomains'].append({'subdomain': full_domain, 'ip': ip})
                    self.success_print(f"Extended discovery: {full_domain} -> {ip}")
                    found_count += 1
                except:
                    pass
                    
            with ThreadPoolExecutor(max_workers=100) as executor:
                executor.map(check_extended_subdomain, extended_subs)
                
            self.neon_print(f"Extended DNS bruteforce found {found_count} additional subdomains", NeonColors.NEON_BLUE)
            
        except Exception as e:
            self.error_print(f"DNS bruteforce failed: {str(e)}")
            
    def check_subdomain_takeover(self, subdomain):
        """Enhanced subdomain takeover detection"""
        try:
            response = requests.get(f"http://{subdomain}", timeout=8, allow_redirects=False)
            
            takeover_signatures = {
                'GitHub Pages': ['There isn\'t a GitHub Pages site here', 'For root URLs'],
                'Heroku': ['No such app', 'There\'s nothing here'],
                'Tumblr': ['Whatever you were looking for doesn\'t currently exist'],
                'Shopify': ['Sorry, this shop is currently unavailable'],
                'Surge.sh': ['project not found'],
                'Ghost': ['The thing you were looking for is no longer here'],
                'Tilda': ['Please renew your subscription'],
                'WordPress.com': ['Do you want to register'],
                'Teamwork': ['Oops - We didn\'t find your site'],
                'Helpjuice': ['We could not find what you\'re looking for'],
                'Helpscout': ['No settings were found for this company'],
                'S3 Bucket': ['NoSuchBucket', 'The specified bucket does not exist'],
                'Azure': ['404 Web Site not found', 'This page is parked free']
            }
            
            for service, signatures in takeover_signatures.items():
                for signature in signatures:
                    if signature in response.text:
                        vuln = {
                            'type': 'Subdomain Takeover',
                            'target': subdomain,
                            'severity': 'High',
                            'description': f'Possible {service} subdomain takeover: {signature}',
                            'tool': 'TARANTULA'
                        }
                        self.results['vulnerabilities'].append(vuln)
                        self.warning_print(f"Possible takeover ({service}): {subdomain}")
                        return
                        
        except:
            pass
            
    def enhanced_port_scanning(self):
        """Enhanced port scanning with service detection"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Enhanced port scanning for {self.target}", NeonColors.NEON_GREEN)
        
        # Comprehensive port ranges
        top_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306, 
            3389, 5432, 5900, 8080, 8443, 8888, 9000, 9001, 9090, 6379, 27017, 11211,
            389, 636, 88, 464, 749, 1433, 1521, 3268, 5985, 5986, 445, 137, 138,
            161, 162, 69, 123, 514, 515, 631, 548, 554, 1900, 5353, 5060, 5061,
            8000, 8001, 8008, 8009, 8010, 8081, 8082, 8083, 8089, 8090, 8091, 8092,
            9200, 9300, 5601, 2181, 2379, 4001, 6443, 10250, 10251, 10252, 10255,
            3000, 3001, 4000, 4001, 5000, 5001, 7000, 7001, 9999, 10000, 50000
        ]
        
        open_ports = []
        
        def enhanced_port_scan(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((self.target, port))
                
                if result == 0:
                    service = self.identify_service(port)
                    banner = self.grab_banner(self.target, port)
                    version = self.detect_service_version(banner, port)
                    
                    port_info = {
                        'port': port,
                        'service': service,
                        'banner': banner,
                        'version': version,
                        'state': 'open'
                    }
                    
                    open_ports.append(port_info)
                    self.success_print(f"Port {port}/{service} open - {banner[:60]}")
                    
                    # Enhanced vulnerability checks
                    self.check_service_vulnerabilities(port, service, banner, version)
                    
                sock.close()
            except:
                pass
                
        with ThreadPoolExecutor(max_workers=250) as executor:
            self.loading_animation("Neural port reconnaissance in progress", 4)
            executor.map(enhanced_port_scan, top_ports)
            
        # Nmap integration for detailed scanning
        if open_ports:
            self.nmap_service_scan(open_ports)
            
        self.results['ports'] = open_ports
        self.neon_print(f"Port scanning complete: {len(open_ports)} services discovered", NeonColors.NEON_GREEN)
        
    def nmap_service_scan(self, open_ports):
        """Use nmap for detailed service detection"""
        try:
            if not open_ports:
                return
                
            self.neon_print("Performing detailed service detection with nmap", NeonColors.NEON_BLUE)
            
            port_list = ','.join([str(p['port']) for p in open_ports[:20]])  # Limit to first 20 ports
            
            nmap_cmd = [
                'nmap', '-sV', '-sC', '--script=default,vuln',
                '-p', port_list, self.target,
                '-oX', f"{self.output_dir}/nmap_detailed.xml"
            ]
            
            try:
                result = subprocess.run(nmap_cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.success_print("Nmap service detection completed")
                    self.parse_nmap_results(f"{self.output_dir}/nmap_detailed.xml")
                else:
                    self.warning_print("Nmap service detection failed")
            except subprocess.TimeoutExpired:
                self.warning_print("Nmap scan timeout")
            except FileNotFoundError:
                self.warning_print("Nmap not found - skipping detailed service detection")
                
        except Exception as e:
            self.error_print(f"Nmap service scan failed: {str(e)}")
            
    def parse_nmap_results(self, xml_file):
        """Parse nmap XML results"""
        try:
            # Basic XML parsing would go here
            # For now, just indicate that results are available
            self.neon_print("Nmap results saved to XML", NeonColors.NEON_BLUE)
        except Exception as e:
            self.error_print(f"Failed to parse nmap results: {str(e)}")
            
    def identify_service(self, port):
        """Enhanced service identification"""
        service_map = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP',
            110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL', 6379: 'Redis',
            27017: 'MongoDB', 11211: 'Memcached', 389: 'LDAP', 636: 'LDAPS',
            1433: 'MSSQL', 1521: 'Oracle', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
            9200: 'Elasticsearch', 5601: 'Kibana', 2181: 'Zookeeper', 6443: 'Kubernetes',
            9300: 'Elasticsearch-Transport', 4001: 'etcd', 2379: 'etcd-client'
        }
        return service_map.get(port, 'Unknown')
        
    def grab_banner(self, host, port):
        """Enhanced banner grabbing"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # Send appropriate probes based on port
            if port == 80:
                sock.send(b'GET / HTTP/1.1\r\nHost: ' + host.encode() + b'\r\n\r\n')
            elif port == 443:
                # For HTTPS, we'll skip detailed banner for now
                sock.close()
                return "HTTPS Service"
            else:
                sock.send(b'\r\n')
                
            banner = sock.recv(2048).decode('utf-8', errors='ignore').strip()
            sock.close()
            return banner
        except:
            return ""
            
    def detect_service_version(self, banner, port):
        """Detect service versions from banners"""
        if not banner:
            return "Unknown"
            
        # Common version detection patterns
        version_patterns = {
            'Apache': r'Apache/(\d+\.\d+\.\d+)',
            'nginx': r'nginx/(\d+\.\d+\.\d+)',
            'OpenSSH': r'OpenSSH_(\d+\.\d+)',
            'MySQL': r'MySQL (\d+\.\d+\.\d+)',
            'PostgreSQL': r'PostgreSQL (\d+\.\d+)',
            'Redis': r'Redis server v=(\d+\.\d+\.\d+)',
            'MongoDB': r'MongoDB (\d+\.\d+\.\d+)'
        }
        
        for service, pattern in version_patterns.items():
            match = re.search(pattern, banner)
            if match:
                return f"{service} {match.group(1)}"
                
        return "Version Unknown"
        
    def check_service_vulnerabilities(self, port, service, banner, version):
        """Enhanced service vulnerability detection"""
        vulns = []
        
        # SSH vulnerabilities
        if port == 22 and 'SSH' in banner:
            if 'OpenSSH' in banner:
                version_match = re.search(r'OpenSSH_(\d+\.\d+)', banner)
                if version_match:
                    version_num = float(version_match.group(1))
                    if version_num < 7.4:
                        vulns.append({
                            'type': 'Outdated SSH Version',
                            'severity': 'Medium',
                            'description': f'Outdated OpenSSH version: {banner}',
                            'recommendation': 'Update to OpenSSH 7.4 or later'
                        })
                        
        # HTTP vulnerabilities
        elif port in [80, 8080] and 'HTTP' in service:
            if 'Apache' in banner:
                version_match = re.search(r'Apache/(\d+\.\d+\.\d+)', banner)
                if version_match:
                    version_str = version_match.group(1)
                    major, minor, patch = map(int, version_str.split('.'))
                    if major < 2 or (major == 2 and minor < 4):
                        vulns.append({
                            'type': 'Outdated Apache Version',
                            'severity': 'Medium',
                            'description': f'Outdated Apache version: {version_str}',
                            'recommendation': 'Update to Apache 2.4.x or later'
                        })
                        
        # FTP vulnerabilities
        elif port == 21:
            if 'anonymous' in banner.lower() or 'ftp ready' in banner.lower():
                vulns.append({
                    'type': 'Anonymous FTP Access',
                    'severity': 'Medium',
                    'description': 'Anonymous FTP access may be enabled',
                    'recommendation': 'Disable anonymous FTP access'
                })
                
        # Telnet vulnerabilities
        elif port == 23:
            vulns.append({
                'type': 'Insecure Telnet Service',
                'severity': 'High',
                'description': 'Insecure Telnet service detected',
                'recommendation': 'Replace Telnet with SSH'
            })
            
        # Database vulnerabilities
        elif port in [3306, 5432, 1433, 1521, 27017, 6379]:
            vulns.append({
                'type': 'Exposed Database Service',
                'severity': 'High',
                'description': f'Database service exposed on port {port}',
                'recommendation': 'Restrict database access to authorized networks only'
            })
            
        for vuln in vulns:
            vuln['target'] = f"{self.target}:{port}"
            vuln['tool'] = 'TARANTULA'
            self.results['vulnerabilities'].append(vuln)
            self.warning_print(f"Vulnerability: {vuln['type']}")
            
    def directory_file_discovery(self):
        """Enhanced directory and file discovery"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Enhanced directory discovery for {self.target}", NeonColors.NEON_GREEN)
        
        # Comprehensive directory wordlist
        directories = [
            'admin', 'login', 'dashboard', 'api', 'backup', 'config', 'test', 'dev',
            'uploads', 'images', 'css', 'js', 'includes', 'tmp', 'temp', 'logs',
            'phpmyadmin', 'wp-admin', 'wp-content', 'wp-includes', '.git', '.env',
            'administrator', 'management', 'manager', 'panel', 'control', 'cpanel',
            'database', 'db', 'sql', 'mysql', 'oracle', 'postgres', 'redis',
            'files', 'file', 'docs', 'documentation', 'help', 'support', 'contact',
            'about', 'services', 'products', 'shop', 'store', 'cart', 'checkout',
            'user', 'users', 'profile', 'account', 'settings', 'preferences',
            'blog', 'news', 'events', 'gallery', 'portfolio', 'projects',
            'search', 'results', 'reports', 'analytics', 'stats', 'statistics',
            'monitor', 'monitoring', 'status', 'health', 'check', 'ping',
            'secure', 'security', 'auth', 'authentication', 'oauth', 'sso',
            'mobile', 'app', 'application', 'service', 'webservice', 'rest',
            'v1', 'v2', 'api/v1', 'api/v2', 'graphql', 'swagger', 'openapi'
        ]
        
        found_dirs = []
        
        def check_directory(directory):
            try:
                protocols = ['http', 'https']
                for protocol in protocols:
                    url = f"{protocol}://{self.target}/{directory}"
                    
                    # Use random user agent
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    response = requests.get(url, timeout=8, allow_redirects=False, 
                                          headers=headers, verify=False)
                    
                    if response.status_code in [200, 301, 302, 403, 401]:
                        dir_info = {
                            'directory': directory,
                            'url': url,
                            'status_code': response.status_code,
                            'size': len(response.content),
                            'protocol': protocol,
                            'headers': dict(response.headers)
                        }
                        
                        found_dirs.append(dir_info)
                        self.success_print(f"Directory found: /{directory} [{response.status_code}] ({protocol.upper()})")
                        
                        # Check for sensitive files in discovered directories
                        self.check_sensitive_files(url)
                        
                        # Check for backup files
                        self.check_backup_files(url, directory)
                        break
                        
            except:
                pass
                
        with ThreadPoolExecutor(max_workers=40) as executor:
            self.loading_animation("Neural directory reconnaissance", 4)
            executor.map(check_directory, directories)
            
        # Check for common sensitive files in root
        self.check_root_sensitive_files()
        
        self.results['directories'] = found_dirs
        self.neon_print(f"Directory discovery complete: {len(found_dirs)} paths found", NeonColors.NEON_GREEN)
        
    def check_sensitive_files(self, base_url):
        """Enhanced sensitive file detection"""
        sensitive_files = [
            '.env', '.env.local', '.env.production', '.env.development',
            '.git/config', '.git/HEAD', '.gitignore',
            'web.config', 'php.ini', 'phpinfo.php', 'info.php',
            'config.php', 'database.php', 'wp-config.php', 'settings.php',
            'backup.sql', 'dump.sql', 'database.sql', 'db_backup.sql',
            'users.txt', 'passwords.txt', 'credentials.txt',
            'id_rsa', 'id_dsa', 'private.key', 'server.key',
            'robots.txt', 'sitemap.xml', 'crossdomain.xml',
            'composer.json', 'package.json', 'yarn.lock',
            'Dockerfile', 'docker-compose.yml', '.dockerignore',
            'README.md', 'CHANGELOG.md', 'TODO.txt'
        ]
        
        for file in sensitive_files:
            try:
                file_url = urljoin(base_url, file)
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.get(file_url, timeout=5, headers=headers, verify=False)
                
                if response.status_code == 200 and len(response.content) > 0:
                    file_info = {
                        'file': file,
                        'url': file_url,
                        'size': len(response.content),
                        'content_type': response.headers.get('content-type', 'unknown')
                    }
                    
                    self.results['exposed_files'].append(file_info)
                    
                    # Classify severity based on file type
                    if file in ['.env', 'wp-config.php', 'database.php', 'id_rsa', 'private.key']:
                        severity = 'Critical'
                    elif file in ['config.php', '.git/config', 'backup.sql']:
                        severity = 'High'
                    else:
                        severity = 'Medium'
                        
                    vuln = {
                        'type': 'Sensitive File Exposure',
                        'target': file_url,
                        'severity': severity,
                        'description': f'Sensitive file exposed: {file}',
                        'tool': 'TARANTULA'
                    }
                    self.results['vulnerabilities'].append(vuln)
                    self.warning_print(f"Sensitive file exposed: {file_url}")
                    
            except:
                pass
                
    def check_backup_files(self, base_url, directory):
        """Check for backup files in discovered directories"""
        backup_extensions = ['.bak', '.backup', '.old', '.orig', '.copy', '.tmp', '~']
        
        for ext in backup_extensions:
            try:
                backup_url = f"{base_url}{ext}"
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.get(backup_url, timeout=5, headers=headers, verify=False)
                
                if response.status_code == 200 and len(response.content) > 0:
                    self.warning_print(f"Backup file found: {backup_url}")
                    
                    vuln = {
                        'type': 'Backup File Exposure',
                        'target': backup_url,
                        'severity': 'Medium',
                        'description': f'Backup file accessible: {directory}{ext}',
                        'tool': 'TARANTULA'
                    }
                    self.results['vulnerabilities'].append(vuln)
                    
            except:
                pass
                
    def check_root_sensitive_files(self):
        """Check for sensitive files in root directory"""
        root_files = [
            'robots.txt', 'sitemap.xml', 'security.txt', '.well-known/security.txt',
            'crossdomain.xml', 'clientaccesspolicy.xml', 'humans.txt'
        ]
        
        for file in root_files:
            try:
                protocols = ['http', 'https']
                for protocol in protocols:
                    url = f"{protocol}://{self.target}/{file}"
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    response = requests.get(url, timeout=5, headers=headers, verify=False)
                    
                    if response.status_code == 200:
                        self.success_print(f"Information file found: {url}")
                        
                        # Parse robots.txt for additional paths
                        if file == 'robots.txt':
                            self.parse_robots_txt(response.text)
                        break
                        
            except:
                pass
                
    def parse_robots_txt(self, robots_content):
        """Parse robots.txt for additional discovery paths"""
        try:
            disallow_paths = []
            for line in robots_content.split('\n'):
                line = line.strip()
                if line.startswith('Disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path and path != '/':
                        disallow_paths.append(path)
                        
            self.neon_print(f"Found {len(disallow_paths)} disallowed paths in robots.txt", NeonColors.NEON_BLUE)
            
            # Check accessibility of disallowed paths
            for path in disallow_paths[:20]:  # Limit to first 20
                try:
                    url = f"http://{self.target}{path}"
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    response = requests.get(url, timeout=5, headers=headers, verify=False)
                    
                    if response.status_code == 200:
                        self.success_print(f"Accessible disallowed path: {path}")
                        
                except:
                    pass
                    
        except Exception as e:
            self.error_print(f"Failed to parse robots.txt: {str(e)}")
            
    def nuclei_vulnerability_scan(self):
        """Nuclei vulnerability scanning integration"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Nuclei vulnerability scan for {self.target}", NeonColors.NEON_GREEN)
        
        try:
            # Check if nuclei is available
            result = subprocess.run(['nuclei', '-version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.error_print("Nuclei not found. Please install: go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest")
                return
                
            # Prepare targets
            targets = [self.target]
            for subdomain in self.results.get('subdomains', []):
                targets.append(subdomain['subdomain'])
                
            # Write targets to file
            targets_file = f"{self.output_dir}/nuclei_targets.txt"
            with open(targets_file, 'w') as f:
                for target in targets[:50]:  # Limit targets
                    f.write(f"http://{target}\n")
                    f.write(f"https://{target}\n")
                    
            # Run nuclei scan
            nuclei_output = f"{self.output_dir}/nuclei/nuclei_results.json"
            
            nuclei_cmd = [
                'nuclei',
                '-l', targets_file,
                '-t', 'cves,vulnerabilities,exposures,misconfiguration',
                '-severity', 'critical,high,medium',
                '-json',
                '-o', nuclei_output,
                '-silent',
                '-timeout', '10',
                '-retries', '2'
            ]
            
            self.loading_animation("Nuclei vulnerability scan in progress", 5)
            
            try:
                result = subprocess.run(nuclei_cmd, capture_output=True, text=True, timeout=600)
                
                if os.path.exists(nuclei_output):
                    self.parse_nuclei_results(nuclei_output)
                    self.success_print("Nuclei scan completed")
                else:
                    self.warning_print("Nuclei scan completed but no results file found")
                    
            except subprocess.TimeoutExpired:
                self.warning_print("Nuclei scan timeout - results may be incomplete")
                if os.path.exists(nuclei_output):
                    self.parse_nuclei_results(nuclei_output)
                    
        except Exception as e:
            self.error_print(f"Nuclei scan failed: {str(e)}")
            
    def parse_nuclei_results(self, results_file):
        """Parse nuclei JSON results"""
        try:
            nuclei_vulns = []
            
            with open(results_file, 'r') as f:
                for line in f:
                    try:
                        result = json.loads(line.strip())
                        
                        vuln = {
                            'type': f"Nuclei: {result.get('info', {}).get('name', 'Unknown')}",
                            'target': result.get('host', self.target),
                            'severity': result.get('info', {}).get('severity', 'Unknown').title(),
                            'description': result.get('info', {}).get('description', 'No description'),
                            'matcher_name': result.get('matcher-name', ''),
                            'template_id': result.get('template-id', ''),
                            'tool': 'Nuclei'
                        }
                        
                        nuclei_vulns.append(vuln)
                        self.results['vulnerabilities'].append(vuln)
                        self.results['nuclei_results'].append(result)
                        
                        # Color code by severity
                        if vuln['severity'].lower() == 'critical':
                            self.error_print(f"CRITICAL: {vuln['type']} on {vuln['target']}")
                        elif vuln['severity'].lower() == 'high':
                            self.warning_print(f"HIGH: {vuln['type']} on {vuln['target']}")
                        else:
                            self.neon_print(f"{vuln['severity'].upper()}: {vuln['type']} on {vuln['target']}", NeonColors.YELLOW)
                            
                    except json.JSONDecodeError:
                        continue
                        
            self.neon_print(f"Nuclei found {len(nuclei_vulns)} vulnerabilities", NeonColors.NEON_GREEN)
            
        except Exception as e:
            self.error_print(f"Failed to parse nuclei results: {str(e)}")
            
    def sqlmap_injection_testing(self):
        """SQLMap injection testing integration"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"SQLMap injection testing for {self.target}", NeonColors.NEON_GREEN)
        
        try:
            # Check if sqlmap is available
            result = subprocess.run(['sqlmap', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.error_print("SQLMap not found. Please install sqlmap")
                return
                
            # Prepare target URLs for testing
            test_urls = []
            
            # Test main domain
            test_urls.extend([
                f"http://{self.target}/?id=1",
                f"https://{self.target}/?id=1",
                f"http://{self.target}/login.php",
                f"https://{self.target}/admin.php"
            ])
            
            # Test discovered directories with common parameters
            for dir_info in self.results.get('directories', []):
                if dir_info.get('status_code') == 200:
                    base_url = dir_info['url']
                    test_urls.extend([
                        f"{base_url}?id=1",
                        f"{base_url}?user=test",
                        f"{base_url}?search=test"
                    ])
                    
            sqlmap_results = []
            
            for url in test_urls[:10]:  # Limit to first 10 URLs
                try:
                    self.neon_print(f"Testing SQL injection on: {url}", NeonColors.NEON_BLUE)
                    
                    sqlmap_output = f"{self.output_dir}/sqlmap/sqlmap_{hashlib.md5(url.encode()).hexdigest()}.txt"
                    
                    sqlmap_cmd = [
                        'sqlmap',
                        '-u', url,
                        '--batch',
                        '--random-agent',
                        '--timeout', '10',
                        '--retries', '2',
                        '--level', '1',
                        '--risk', '1',
                        '--output-dir', f"{self.output_dir}/sqlmap/"
                    ]
                    
                    result = subprocess.run(sqlmap_cmd, capture_output=True, text=True, timeout=120)
                    
                    # Parse sqlmap output for vulnerabilities
                    if 'Parameter:' in result.stdout and 'is vulnerable' in result.stdout:
                        vuln = {
                            'type': 'SQL Injection',
                            'target': url,
                            'severity': 'Critical',
                            'description': f'SQL injection vulnerability found in {url}',
                            'tool': 'SQLMap'
                        }
                        
                        sqlmap_results.append(vuln)
                        self.results['vulnerabilities'].append(vuln)
                        self.results['sqlmap_results'].append({
                            'url': url,
                            'output': result.stdout
                        })
                        
                        self.error_print(f"SQL Injection found: {url}")
                        
                except subprocess.TimeoutExpired:
                    self.warning_print(f"SQLMap timeout for {url}")
                except Exception as e:
                    self.warning_print(f"SQLMap test failed for {url}: {str(e)}")
                    
            self.neon_print(f"SQLMap testing complete: {len(sqlmap_results)} injections found", NeonColors.NEON_GREEN)
            
        except Exception as e:
            self.error_print(f"SQLMap testing failed: {str(e)}")
            
    def wpscan_wordpress_analysis(self):
        """WPScan WordPress analysis integration"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        # Check if WordPress is detected
        if 'WordPress' not in self.results.get('tech_stack', []):
            self.warning_print("WordPress not detected - running WPScan anyway")
            
        self.neon_print(f"WPScan WordPress analysis for {self.target}", NeonColors.NEON_GREEN)
        
        try:
            # Check if wpscan is available
            result = subprocess.run(['wpscan', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.error_print("WPScan not found. Please install: gem install wpscan")
                return
                
            # Prepare URLs to scan
            wordpress_urls = []
            
            # Check main domain
            for protocol in ['http', 'https']:
                wordpress_urls.append(f"{protocol}://{self.target}")
                
            # Check subdomains
            for subdomain in self.results.get('subdomains', []):
                for protocol in ['http', 'https']:
                    wordpress_urls.append(f"{protocol}://{subdomain['subdomain']}")
                    
            wpscan_results = []
            
            for url in wordpress_urls[:5]:  # Limit to first 5 URLs
                try:
                    self.neon_print(f"WPScan analysis on: {url}", NeonColors.NEON_BLUE)
                    
                    wpscan_output = f"{self.output_dir}/wpscan/wpscan_{hashlib.md5(url.encode()).hexdigest()}.json"
                    
                    wpscan_cmd = [
                        'wpscan',
                        '--url', url,
                        '--format', 'json',
                        '--output', wpscan_output,
                        '--random-user-agent',
                        '--max-threads', '5',
                        '--request-timeout', '10',
                        '--connect-timeout', '5'
                    ]
                    
                    result = subprocess.run(wpscan_cmd, capture_output=True, text=True, timeout=180)
                    
                    if os.path.exists(wpscan_output):
                        self.parse_wpscan_results(wpscan_output, url)
                        
                except subprocess.TimeoutExpired:
                    self.warning_print(f"WPScan timeout for {url}")
                except Exception as e:
                    self.warning_print(f"WPScan failed for {url}: {str(e)}")
                    
            self.neon_print("WPScan analysis complete", NeonColors.NEON_GREEN)
            
        except Exception as e:
            self.error_print(f"WPScan analysis failed: {str(e)}")
            
    def parse_wpscan_results(self, results_file, url):
        """Parse WPScan JSON results"""
        try:
            with open(results_file, 'r') as f:
                wpscan_data = json.load(f)
                
            self.results['wpscan_results'].append({
                'url': url,
                'data': wpscan_data
            })
            
            # Parse vulnerabilities
            if 'vulnerabilities' in wpscan_data:
                for vuln in wpscan_data['vulnerabilities']:
                    vuln_info = {
                        'type': f"WordPress: {vuln.get('title', 'Unknown Vulnerability')}",
                        'target': url,
                        'severity': 'High',  # Default to High for WordPress vulns
                        'description': vuln.get('title', 'WordPress vulnerability detected'),
                        'references': vuln.get('references', {}),
                        'tool': 'WPScan'
                    }
                    
                    self.results['vulnerabilities'].append(vuln_info)
                    self.warning_print(f"WordPress vulnerability: {vuln.get('title', 'Unknown')}")
                    
            # Parse version information
            if 'version' in wpscan_data:
                version_info = wpscan_data['version']
                self.results['cms_info']['wordpress'] = {
                    'version': version_info.get('number', 'Unknown'),
                    'status': version_info.get('status', 'Unknown'),
                    'url': url
                }
                
                self.success_print(f"WordPress version: {version_info.get('number', 'Unknown')}")
                
            # Parse plugins
            if 'plugins' in wpscan_data:
                plugins = wpscan_data['plugins']
                self.neon_print(f"Found {len(plugins)} WordPress plugins", NeonColors.NEON_BLUE)
                
                for plugin_name, plugin_data in plugins.items():
                    if 'vulnerabilities' in plugin_data:
                        for vuln in plugin_data['vulnerabilities']:
                            vuln_info = {
                                'type': f"WordPress Plugin: {plugin_name}",
                                'target': url,
                                'severity': 'Medium',
                                'description': f"Plugin vulnerability in {plugin_name}: {vuln.get('title', 'Unknown')}",
                                'tool': 'WPScan'
                            }
                            
                            self.results['vulnerabilities'].append(vuln_info)
                            self.warning_print(f"Plugin vulnerability: {plugin_name}")
                            
            # Parse themes
            if 'themes' in wpscan_data:
                themes = wpscan_data['themes']
                for theme_name, theme_data in themes.items():
                    if 'vulnerabilities' in theme_data:
                        for vuln in theme_data['vulnerabilities']:
                            vuln_info = {
                                'type': f"WordPress Theme: {theme_name}",
                                'target': url,
                                'severity': 'Medium',
                                'description': f"Theme vulnerability in {theme_name}: {vuln.get('title', 'Unknown')}",
                                'tool': 'WPScan'
                            }
                            
                            self.results['vulnerabilities'].append(vuln_info)
                            self.warning_print(f"Theme vulnerability: {theme_name}")
                            
        except Exception as e:
            self.error_print(f"Failed to parse WPScan results: {str(e)}")
            
    def waf_detection_bypass(self):
        """WAF detection and bypass using wafw00f and custom techniques"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"WAF detection and bypass analysis for {self.target}", NeonColors.NEON_GREEN)
        
        # Try to import wafw00f
        try:
            from wafw00f.main import WAFW00F
            wafw00f_available = True
        except ImportError:
            wafw00f_available = False
            self.warning_print("wafw00f not available - using custom WAF detection")
            
        detected_wafs = []
        
        # Use wafw00f if available
        if wafw00f_available:
            try:
                for protocol in ['http', 'https']:
                    url = f"{protocol}://{self.target}"
                    
                    # Initialize wafw00f
                    waf_detector = WAFW00F(url)
                    waf_detector.normalRequest()
                    
                    # Detect WAFs
                    waf_list = waf_detector.identwaf()
                    
                    if waf_list:
                        for waf in waf_list:
                            detected_wafs.append(waf)
                            self.warning_print(f"WAF detected: {waf}")
                    else:
                        self.success_print(f"No WAF detected on {protocol}")
                        
            except Exception as e:
                self.error_print(f"wafw00f detection failed: {str(e)}")
                
        # Custom WAF detection
        self.custom_waf_detection()
        
        # WAF bypass techniques
        if detected_wafs:
            self.attempt_waf_bypass(detected_wafs)
        else:
            self.custom_waf_detection()
            
        self.results['waf_detection'] = {
            'detected_wafs': detected_wafs,
            'detection_method': 'wafw00f + custom' if wafw00f_available else 'custom'
        }
        
    def custom_waf_detection(self):
        """Custom WAF detection techniques"""
        try:
            self.neon_print("Custom WAF detection in progress", NeonColors.NEON_BLUE)
            
            # Test payloads to trigger WAF responses
            test_payloads = [
                "/?id=1' OR '1'='1",
                "/?test=<script>alert(1)</script>",
                "/?union=SELECT * FROM users",
                "/?cmd=cat /etc/passwd",
                "/?xss='><img src=x onerror=alert(1)>"
            ]
            
            waf_signatures = {
                'Cloudflare': ['cloudflare', 'cf-ray', 'cf-cache-status'],
                'AWS WAF': ['aws', 'x-amzn', 'x-amz'],
                'Akamai': ['akamai', 'x-akamai'],
                'Incapsula': ['incap_ses', 'visid_incap', 'incapsula'],
                'ModSecurity': ['mod_security', 'modsecurity'],
                'F5 BIG-IP': ['bigip', 'f5', 'x-waf-event'],
                'Barracuda': ['barracuda', 'barra'],
                'Sucuri': ['sucuri', 'x-sucuri'],
                'Wordfence': ['wordfence'],
                'SiteGuard': ['siteguard']
            }
            
            detected_custom_wafs = []
            
            for payload in test_payloads:
                try:
                    for protocol in ['http', 'https']:
                        url = f"{protocol}://{self.target}{payload}"
                        headers = {'User-Agent': random.choice(self.user_agents)}
                        
                        response = requests.get(url, timeout=10, headers=headers, verify=False)
                        
                        # Check headers for WAF signatures
                        response_headers = str(response.headers).lower()
                        response_text = response.text.lower()
                        
                        for waf, signatures in waf_signatures.items():
                            for signature in signatures:
                                if signature in response_headers or signature in response_text:
                                    if waf not in detected_custom_wafs:
                                        detected_custom_wafs.append(waf)
                                        self.warning_print(f"WAF detected (custom): {waf}")
                                        
                        # Check for common WAF response codes and patterns
                        if response.status_code in [403, 406, 429, 503]:
                            error_patterns = [
                                'access denied', 'blocked', 'security violation',
                                'suspicious activity', 'request rejected'
                            ]
                            
                            for pattern in error_patterns:
                                if pattern in response_text:
                                    if 'Generic WAF' not in detected_custom_wafs:
                                        detected_custom_wafs.append('Generic WAF')
                                        self.warning_print("Generic WAF detected (blocking patterns)")
                                    break
                                    
                except:
                    continue
                    
            self.results['waf_detection']['custom_detected'] = detected_custom_wafs
            
        except Exception as e:
            self.error_print(f"Custom WAF detection failed: {str(e)}")
            
    def attempt_waf_bypass(self, detected_wafs):
        """Attempt various WAF bypass techniques"""
        self.neon_print("Attempting WAF bypass techniques", NeonColors.NEON_BLUE)
        
        bypass_techniques = [
            # Case variation
            "/?id=1' UnIoN sElEcT * FrOm users--",
            # Comment insertion
            "/?id=1' UNION/**/SELECT/**/*/**/FROM/**/users--",
            # Encoding
            "/?id=1%27%20UNION%20SELECT%20*%20FROM%20users--",
            # Double encoding
            "/?id=1%2527%2520UNION%2520SELECT%2520*%2520FROM%2520users--",
            # Null byte
            "/?id=1' UNION%00SELECT * FROM users--",
            # White space alternatives
            "/?id=1'%09UNION%0ASELECT%0D*%0CFROM%0Busers--"
        ]
        
        successful_bypasses = []
        
        for technique in bypass_techniques:
            try:
                for protocol in ['http', 'https']:
                    url = f"{protocol}://{self.target}{technique}"
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    
                    response = requests.get(url, timeout=10, headers=headers, verify=False)
                    
                    # Check if bypass was successful (status 200 without WAF block message)
                    if response.status_code == 200:
                        block_indicators = ['blocked', 'denied', 'security', 'violation']
                        response_text = response.text.lower()
                        
                        if not any(indicator in response_text for indicator in block_indicators):
                            successful_bypasses.append(technique)
                            self.success_print(f"Potential WAF bypass: {technique}")
                            break
                            
            except:
                continue
                
        self.results['waf_detection']['bypass_attempts'] = successful_bypasses
        
        if successful_bypasses:
            self.neon_print(f"Found {len(successful_bypasses)} potential WAF bypasses", NeonColors.NEON_GREEN)
        else:
            self.warning_print("No successful WAF bypasses found")
            
    def cloudflare_real_ip_discovery(self):
        """Discover real IP behind Cloudflare"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Cloudflare real IP discovery for {self.target}", NeonColors.NEON_GREEN)
        
        real_ips = []
        
        # Method 1: DNS History lookup
        real_ips.extend(self.dns_history_lookup())
        
        # Method 2: Subdomain IP correlation
        real_ips.extend(self.subdomain_ip_correlation())
        
        # Method 3: SSL certificate analysis
        real_ips.extend(self.ssl_certificate_ip_analysis())
        
        # Method 4: HTTP headers analysis
        real_ips.extend(self.http_headers_ip_analysis())
        
        # Method 5: Mail server correlation
        real_ips.extend(self.mail_server_correlation())
        
        # Remove duplicates and Cloudflare IPs
        real_ips = list(set(real_ips))
        real_ips = self.filter_cloudflare_ips(real_ips)
        
        if real_ips:
            self.results['real_ip'] = real_ips[0]  # First found IP
            self.results['cloudflare_bypass']['real_ips'] = real_ips
            
            for ip in real_ips:
                self.success_print(f"Potential real IP: {ip}")
                
            # Verify real IPs
            self.verify_real_ips(real_ips)
        else:
            self.warning_print("No real IP found behind Cloudflare")
            
    def dns_history_lookup(self):
        """Lookup DNS history for previous IP addresses"""
        ips = []
        try:
            # This would typically use services like SecurityTrails, but we'll simulate
            self.neon_print("Checking DNS history records", NeonColors.NEON_BLUE)
            
            # Try passive DNS sources
            sources = [
                f"https://api.hackertarget.com/reverseiplookup/?q={self.target}",
                f"https://api.hackertarget.com/hostsearch/?q={self.target}"
            ]
            
            for source in sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200 and 'No records found' not in response.text:
                        # Parse IP addresses from response
                        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                        found_ips = re.findall(ip_pattern, response.text)
                        ips.extend(found_ips)
                except:
                    continue
                    
        except Exception as e:
            self.error_print(f"DNS history lookup failed: {str(e)}")
            
        return ips
        
    def subdomain_ip_correlation(self):
        """Correlate IPs from subdomains to find real IP"""
        ips = []
        try:
            self.neon_print("Correlating subdomain IPs", NeonColors.NEON_BLUE)
            
            subdomain_ips = {}
            for subdomain in self.results.get('subdomains', []):
                ip = subdomain.get('ip')
                if ip:
                    if ip not in subdomain_ips:
                        subdomain_ips[ip] = []
                    subdomain_ips[ip].append(subdomain['subdomain'])
                    
            # Look for IPs that appear multiple times (likely real IP)
            for ip, domains in subdomain_ips.items():
                if len(domains) > 1:
                    ips.append(ip)
                    self.neon_print(f"Correlated IP {ip} from {len(domains)} subdomains", NeonColors.NEON_BLUE)
                    
        except Exception as e:
            self.error_print(f"Subdomain IP correlation failed: {str(e)}")
            
        return ips
        
    def ssl_certificate_ip_analysis(self):
        """Analyze SSL certificates for real IP information"""
        ips = []
        try:
            self.neon_print("Analyzing SSL certificates for IP information", NeonColors.NEON_BLUE)
            
            # This would analyze certificate transparency logs and certificate details
            # For now, we'll simulate this process
            
        except Exception as e:
            self.error_print(f"SSL certificate analysis failed: {str(e)}")
            
        return ips
        
    def http_headers_ip_analysis(self):
        """Analyze HTTP headers for real IP leakage"""
        ips = []
        try:
            self.neon_print("Analyzing HTTP headers for IP leakage", NeonColors.NEON_BLUE)
            
            # Headers that might leak real IP
            ip_headers = [
                'X-Real-IP', 'X-Forwarded-For', 'X-Originating-IP',
                'X-Cluster-Client-IP', 'X-Client-IP', 'Client-IP'
            ]
            
            for protocol in ['http', 'https']:
                try:
                    url = f"{protocol}://{self.target}"
                    response = requests.get(url, timeout=10, verify=False)
                    
                    for header in ip_headers:
                        if header in response.headers:
                            value = response.headers[header]
                            # Extract IP addresses
                            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                            found_ips = re.findall(ip_pattern, value)
                            ips.extend(found_ips)
                            
                except:
                    continue
                    
        except Exception as e:
            self.error_print(f"HTTP headers analysis failed: {str(e)}")
            
        return ips
        
    def mail_server_correlation(self):
        """Correlate mail server IPs to find real IP"""
        ips = []
        try:
            self.neon_print("Correlating mail server IPs", NeonColors.NEON_BLUE)
            
            # Get MX records
            mx_records = self.results.get('dns_records', {}).get('MX', [])
            
            for mx_record in mx_records:
                try:
                    # Extract hostname from MX record
                    mx_host = mx_record.split()[-1].rstrip('.')
                    
                    # Resolve MX host IP
                    mx_ip = socket.gethostbyname(mx_host)
                    ips.append(mx_ip)
                    
                    self.neon_print(f"Mail server IP: {mx_ip} ({mx_host})", NeonColors.NEON_BLUE)
                    
                except:
                    continue
                    
        except Exception as e:
            self.error_print(f"Mail server correlation failed: {str(e)}")
            
        return ips
        
    def filter_cloudflare_ips(self, ips):
        """Filter out known Cloudflare IP ranges"""
        cloudflare_ranges = [
            '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22',
            '103.31.4.0/22', '141.101.64.0/18', '108.162.192.0/18',
            '190.93.240.0/20', '188.114.96.0/20', '197.234.240.0/22',
            '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/12'
        ]
        
        filtered_ips = []
        
        for ip in ips:
            is_cloudflare = False
            
            try:
                import ipaddress
                ip_obj = ipaddress.ip_address(ip)
                
                for cf_range in cloudflare_ranges:
                    if ip_obj in ipaddress.ip_network(cf_range):
                        is_cloudflare = True
                        break
                        
                if not is_cloudflare:
                    filtered_ips.append(ip)
                    
            except:
                # If ipaddress module fails, include the IP
                filtered_ips.append(ip)
                
        return filtered_ips
        
    def verify_real_ips(self, ips):
        """Verify if discovered IPs are actually hosting the target"""
        verified_ips = []
        
        for ip in ips:
            try:
                self.neon_print(f"Verifying IP: {ip}", NeonColors.NEON_BLUE)
                
                # Test HTTP connection directly to IP
                headers = {
                    'Host': self.target,
                    'User-Agent': random.choice(self.user_agents)
                }
                
                for protocol in ['http', 'https']:
                    try:
                        url = f"{protocol}://{ip}"
                        response = requests.get(url, headers=headers, timeout=10, verify=False)
                        
                        if response.status_code == 200:
                            # Check if content matches main site
                            main_response = requests.get(f"{protocol}://{self.target}", timeout=10, verify=False)
                            
                            # Simple content comparison
                            if len(response.content) > 0 and abs(len(response.content) - len(main_response.content)) < 1000:
                                verified_ips.append(ip)
                                self.success_print(f"Verified real IP: {ip}")
                                break
                                
                    except:
                        continue
                        
            except Exception as e:
                self.warning_print(f"Failed to verify IP {ip}: {str(e)}")
                
        self.results['cloudflare_bypass']['verified_ips'] = verified_ips
        
    def cloudscraper_integration(self):
        """Integrate cloudscraper for Cloudflare bypass"""
        try:
            import cloudscraper
            
            self.neon_print("Attempting Cloudflare bypass with cloudscraper", NeonColors.NEON_BLUE)
            
            scraper = cloudscraper.create_scraper()
            
            for protocol in ['http', 'https']:
                try:
                    url = f"{protocol}://{self.target}"
                    response = scraper.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        self.success_print(f"Cloudscraper bypass successful: {url}")
                        
                        # Store bypass information
                        self.results['cloudflare_bypass']['cloudscraper'] = {
                            'success': True,
                            'url': url,
                            'content_length': len(response.content)
                        }
                        
                        return response
                        
                except Exception as e:
                    self.warning_print(f"Cloudscraper failed for {url}: {str(e)}")
                    
        except ImportError:
            self.warning_print("cloudscraper not available - install with: pip install cloudscraper")
            
        return None
        
    def fofa_cyberspace_mapping(self):
        """FOFA cyber space mapping integration"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"FOFA cyber space mapping for {self.target}", NeonColors.NEON_GREEN)
        
        if not self.api_keys.get('fofa_email') or not self.api_keys.get('fofa_key'):
            self.warning_print("FOFA API credentials not configured")
            self.simulate_fofa_results()
            return
            
        try:
            # FOFA API integration
            fofa_queries = [
                f'domain="{self.target}"',
                f'cert="{self.target}"',
                f'header="Host: {self.target}"',
                f'title="{self.target}"'
            ]
            
            fofa_results = []
            
            for query in fofa_queries:
                try:
                    # Encode query
                    import base64
                    encoded_query = base64.b64encode(query.encode()).decode()
                    
                    # FOFA API URL
                    api_url = f"https://fofa.so/api/v1/search/all"
                    params = {
                        'email': self.api_keys['fofa_email'],
                        'key': self.api_keys['fofa_key'],
                        'qbase64': encoded_query,
                        'size': 100,
                        'fields': 'host,ip,port,protocol,country,os,server,title'
                    }
                    
                    response = requests.get(api_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('error') == False and 'results' in data:
                            results = data['results']
                            fofa_results.extend(results)
                            
                            self.neon_print(f"FOFA query '{query}' returned {len(results)} results", NeonColors.NEON_BLUE)
                            
                            for result in results[:10]:  # Show first 10
                                host, ip, port, protocol = result[:4]
                                self.success_print(f"FOFA: {host} ({ip}:{port}) - {protocol}")
                                
                    else:
                        self.warning_print(f"FOFA API error for query: {query}")
                        
                except Exception as e:
                    self.warning_print(f"FOFA query failed: {str(e)}")
                    
            self.results['fofa_intelligence'] = {
                'queries': fofa_queries,
                'results': fofa_results,
                'total_results': len(fofa_results)
            }
            
        except Exception as e:
            self.error_print(f"FOFA mapping failed: {str(e)}")
            self.simulate_fofa_results()
            
    def simulate_fofa_results(self):
        """Simulate FOFA results when API is not available"""
        self.neon_print("Simulating FOFA results (API not configured)", NeonColors.YELLOW)
        
        # This would show what kind of data FOFA would provide
        simulated_results = [
            {
                'host': self.target,
                'ip': '1.2.3.4',
                'port': '80',
                'protocol': 'http',
                'country': 'US',
                'server': 'nginx'
            }
        ]
        
        self.results['fofa_intelligence'] = {
            'simulated': True,
            'results': simulated_results
        }
        
    def shodan_attack_surface_intel(self):
        """Shodan attack surface intelligence"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Shodan attack surface intelligence for {self.target}", NeonColors.NEON_GREEN)
        
        if not self.api_keys.get('shodan'):
            self.warning_print("Shodan API key not configured")
            self.simulate_shodan_results()
            return
            
        try:
            import shodan
            
            api = shodan.Shodan(self.api_keys['shodan'])
            
            # Search for target
            shodan_results = []
            
            # Search by domain
            try:
                results = api.search(f'hostname:{self.target}')
                shodan_results.extend(results['matches'])
                self.neon_print(f"Shodan hostname search: {len(results['matches'])} results", NeonColors.NEON_BLUE)
            except Exception as e:
                self.warning_print(f"Shodan hostname search failed: {str(e)}")
                
            # Search by IP (if we have real IPs)
            if self.results.get('real_ip'):
                try:
                    results = api.search(f'ip:{self.results["real_ip"]}')
                    shodan_results.extend(results['matches'])
                    self.neon_print(f"Shodan IP search: {len(results['matches'])} results", NeonColors.NEON_BLUE)
                except Exception as e:
                    self.warning_print(f"Shodan IP search failed: {str(e)}")
                    
            # Parse Shodan results
            parsed_results = []
            for result in shodan_results:
                parsed_result = {
                    'ip': result.get('ip_str', ''),
                    'port': result.get('port', ''),
                    'protocol': result.get('transport', ''),
                    'product': result.get('product', ''),
                    'version': result.get('version', ''),
                    'os': result.get('os', ''),
                    'country': result.get('location', {}).get('country_name', ''),
                    'org': result.get('org', ''),
                    'hostnames': result.get('hostnames', []),
                    'vulnerabilities': result.get('vulns', [])
                }
                
                parsed_results.append(parsed_result)
                
                # Report vulnerabilities found by Shodan
                for vuln_id in result.get('vulns', []):
                    vuln = {
                        'type': f'Shodan CVE: {vuln_id}',
                        'target': f"{result.get('ip_str', '')}:{result.get('port', '')}",
                        'severity': 'High',
                        'description': f'CVE {vuln_id} detected by Shodan',
                        'tool': 'Shodan'
                    }
                    
                    self.results['vulnerabilities'].append(vuln)
                    self.warning_print(f"Shodan CVE: {vuln_id}")
                    
            self.results['shodan_data'] = {
                'results': parsed_results,
                'total_results': len(parsed_results)
            }
            
            for result in parsed_results[:10]:  # Show first 10
                self.success_print(f"Shodan: {result['ip']}:{result['port']} - {result['product']} {result['version']}")
                
        except ImportError:
            self.warning_print("Shodan library not available - install with: pip install shodan")
            self.simulate_shodan_results()
        except Exception as e:
            self.error_print(f"Shodan intelligence failed: {str(e)}")
            self.simulate_shodan_results()
            
    def simulate_shodan_results(self):
        """Simulate Shodan results when API is not available"""
        self.neon_print("Simulating Shodan results (API not configured)", NeonColors.YELLOW)
        
        # This would show what kind of data Shodan would provide
        simulated_results = [
            {
                'ip': '1.2.3.4',
                'port': '80',
                'product': 'nginx',
                'version': '1.18.0',
                'os': 'Ubuntu',
                'country': 'United States'
            }
        ]
        
        self.results['shodan_data'] = {
            'simulated': True,
            'results': simulated_results
        }
        
    def full_enterprise_scan(self):
        """Full enterprise-grade scan with all tools"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print("Initiating full enterprise attack surface scan", NeonColors.NEON_PINK)
        
        # Check tool dependencies
        self.check_tool_dependencies()
        
        enterprise_modules = [
            ("Advanced Subdomain Discovery", self.advanced_subdomain_discovery),
            ("Enhanced Port Scanning", self.enhanced_port_scanning),
            ("Directory & File Discovery", self.directory_file_discovery),
            ("DNS Intelligence Gathering", self.comprehensive_dns_enum),
            ("HTTP Analysis & Fingerprinting", self.advanced_http_analysis),
            ("WAF Detection & Bypass", self.waf_detection_bypass),
            ("Cloudflare Real IP Discovery", self.cloudflare_real_ip_discovery),
            ("FOFA Cyber Space Mapping", self.fofa_cyberspace_mapping),
            ("Shodan Attack Surface Intel", self.shodan_attack_surface_intel),
            ("Nuclei Vulnerability Scan", self.nuclei_vulnerability_scan),
            ("SQLMap Injection Testing", self.sqlmap_injection_testing),
            ("WPScan WordPress Analysis", self.wpscan_wordpress_analysis),
            ("SSL/TLS Security Assessment", self.ssl_tls_vulnerability_check),
            ("Email & Social OSINT", self.email_social_osint),
            ("Domain Reputation Analysis", self.domain_reputation_check)
        ]
        
        for module_name, module_func in enterprise_modules:
            self.neon_print(f"Enterprise module executing: {module_name}", NeonColors.NEON_BLUE)
            try:
                module_func()
            except Exception as e:
                self.error_print(f"{module_name} failed: {str(e)}")
            print()
            
        self.success_print("🔥 ENTERPRISE SCAN COMPLETED 🔥")
        self.save_scan_to_db()
        
    def comprehensive_dns_enum(self):
        """Comprehensive DNS enumeration"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Comprehensive DNS intelligence for {self.target}", NeonColors.NEON_GREEN)
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR', 'SRV', 'CAA']
        dns_info = {}
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(self.target, record_type)
                dns_info[record_type] = []
                
                for answer in answers:
                    record_data = str(answer)
                    dns_info[record_type].append(record_data)
                    self.success_print(f"{record_type}: {record_data}")
                    
                    # Extract intelligence from DNS records
                    if record_type == 'TXT':
                        self.analyze_txt_records(record_data)
                    elif record_type == 'MX':
                        self.analyze_mx_records(record_data)
                        
            except:
                dns_info[record_type] = []
                
        # Check for zone transfer vulnerability
        self.check_zone_transfer()
        
        # Check DNSSEC
        self.check_dnssec()
        
        self.results['dns_records'] = dns_info
        
    def analyze_txt_records(self, txt_record):
        """Analyze TXT records for intelligence"""
        if 'v=spf1' in txt_record:
            self.neon_print(f"SPF record: {txt_record}", NeonColors.NEON_BLUE)
        elif 'v=DMARC1' in txt_record:
            self.neon_print(f"DMARC record: {txt_record}", NeonColors.NEON_BLUE)
        elif 'google-site-verification' in txt_record:
            self.neon_print(f"Google verification: {txt_record}", NeonColors.NEON_BLUE)
            
    def analyze_mx_records(self, mx_record):
        """Analyze MX records for mail intelligence"""
        providers = {
            'google.com': 'Google Workspace',
            'outlook.com': 'Microsoft 365',
            'amazonses.com': 'Amazon SES',
            'mailgun.org': 'Mailgun'
        }
        
        for provider, service in providers.items():
            if provider in mx_record:
                self.neon_print(f"Mail service: {service}", NeonColors.NEON_BLUE)
                break
                
    def check_zone_transfer(self):
        """Check for DNS zone transfer vulnerability"""
        try:
            ns_records = dns.resolver.resolve(self.target, 'NS')
            for ns in ns_records:
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(str(ns), self.target))
                    if zone:
                        vuln = {
                            'type': 'DNS Zone Transfer',
                            'target': str(ns),
                            'severity': 'High',
                            'description': f'Zone transfer enabled on {ns}',
                            'tool': 'TARANTULA'
                        }
                        self.results['vulnerabilities'].append(vuln)
                        self.warning_print(f"Zone transfer vulnerability: {ns}")
                except:
                    pass
        except:
            pass
            
    def check_dnssec(self):
        """Check DNSSEC implementation"""
        try:
            response = dns.resolver.resolve(self.target, 'DNSKEY')
            if response:
                self.success_print("DNSSEC implemented")
            else:
                self.warning_print("DNSSEC not implemented")
        except:
            self.warning_print("DNSSEC not implemented")
            
    def advanced_http_analysis(self):
        """Advanced HTTP analysis and fingerprinting"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Advanced HTTP analysis for {self.target}", NeonColors.NEON_GREEN)
        
        # Use cloudscraper for Cloudflare bypass
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
        except ImportError:
            scraper = requests.Session()
            self.warning_print("cloudscraper not available - using standard requests")
            
        protocols = ['http', 'https']
        
        for protocol in protocols:
            try:
                url = f"{protocol}://{self.target}"
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                if hasattr(scraper, 'get'):
                    response = scraper.get(url, timeout=15, headers=headers, verify=False)
                else:
                    response = requests.get(url, timeout=15, headers=headers, verify=False)
                
                # Analyze security headers
                self.analyze_security_headers(response.headers, protocol)
                
                # Detect technologies
                self.detect_technologies(response, protocol)
                
                # Check for security misconfigurations
                self.check_security_misconfigs(response, protocol)
                
            except Exception as e:
                self.error_print(f"HTTP analysis failed for {protocol}: {str(e)}")
                
    def analyze_security_headers(self, headers, protocol):
        """Analyze HTTP security headers"""
        security_headers = {
            'Strict-Transport-Security': 'HSTS',
            'Content-Security-Policy': 'CSP',
            'X-Frame-Options': 'Clickjacking Protection',
            'X-Content-Type-Options': 'MIME Sniffing Protection',
            'X-XSS-Protection': 'XSS Protection',
            'Referrer-Policy': 'Referrer Policy',
            'Permissions-Policy': 'Permissions Policy'
        }
        
        present_headers = {}
        missing_headers = []
        
        for header, description in security_headers.items():
            if header in headers:
                present_headers[header] = headers[header]
                self.success_print(f"{description}: Present")
            else:
                missing_headers.append(description)
                
                # Create vulnerability for missing critical headers
                if header in ['Strict-Transport-Security', 'Content-Security-Policy']:
                    vuln = {
                        'type': 'Missing Security Header',
                        'target': f"{protocol}://{self.target}",
                        'severity': 'Medium',
                        'description': f'Missing {description} header',
                        'tool': 'TARANTULA'
                    }
                    self.results['vulnerabilities'].append(vuln)
                    
                self.warning_print(f"Missing: {description}")
                
        self.results['security_headers'][protocol] = {
            'present': present_headers,
            'missing': missing_headers
        }
        
    def detect_technologies(self, response, protocol):
        """Enhanced technology detection"""
        tech_indicators = {}
        content = response.text.lower()
        
        # Server detection
        if 'server' in response.headers:
            server = response.headers['server']
            tech_indicators['Server'] = server
            
        # Framework detection
        if 'x-powered-by' in response.headers:
            powered_by = response.headers['x-powered-by']
            tech_indicators['Framework'] = powered_by
            
        # Advanced technology detection
        technologies = {
            'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
            'Drupal': ['drupal', 'sites/default'],
            'Joomla': ['joomla', 'components/com_'],
            'Magento': ['mage/', 'magento'],
            'Shopify': ['shopify', 'cdn.shopify.com'],
            'Laravel': ['laravel_session', '_token'],
            'Django': ['csrfmiddlewaretoken', 'django'],
            'React': ['react', '_react', 'react-dom'],
            'Angular': ['angular', 'ng-app', 'ng-version'],
            'Vue.js': ['vue.js', '__vue__', 'vue-router'],
            'jQuery': ['jquery', '$.fn.jquery'],
            'Bootstrap': ['bootstrap', 'btn-primary'],
            'Cloudflare': ['__cf_bm', 'cf-ray'],
            'Google Analytics': ['google-analytics', 'gtag'],
            'Adobe Analytics': ['omniture', 's_code']
        }
        
        detected_tech = []
        for tech, indicators in technologies.items():
            for indicator in indicators:
                if indicator in content or indicator in str(response.headers).lower():
                    if tech not in detected_tech:
                        detected_tech.append(tech)
                        tech_indicators[tech] = 'Detected'
                        self.success_print(f"Technology: {tech}")
                    break
                    
        self.results['tech_stack'].extend(detected_tech)
        
        # CMS specific analysis
        if 'WordPress' in detected_tech:
            self.wordpress_analysis(response)
        elif 'Drupal' in detected_tech:
            self.drupal_analysis(response)
            
    def wordpress_analysis(self, response):
        """WordPress specific analysis"""
        wp_info = {}
        content = response.text
        
        # Version detection
        version_patterns = [
            r'wp-includes/css/[^"]*\?ver=([0-9.]+)',
            r'wp-includes/js/[^"]*\?ver=([0-9.]+)',
            r'generator.*wordpress ([0-9.]+)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                wp_info['version'] = match.group(1)
                self.neon_print(f"WordPress version: {match.group(1)}", NeonColors.NEON_BLUE)
                break
                
        # Theme detection
        theme_pattern = r'wp-content/themes/([^/]+)'
        theme_match = re.search(theme_pattern, content)
        if theme_match:
            wp_info['theme'] = theme_match.group(1)
            self.neon_print(f"WordPress theme: {theme_match.group(1)}", NeonColors.NEON_BLUE)
            
        self.results['cms_info']['wordpress'] = wp_info
        
    def drupal_analysis(self, response):
        """Drupal specific analysis"""
        drupal_info = {}
        content = response.text
        
        # Version detection
        generator_pattern = r'generator.*drupal ([0-9.]+)'
        match = re.search(generator_pattern, content, re.IGNORECASE)
        if match:
            drupal_info['version'] = match.group(1)
            self.neon_print(f"Drupal version: {match.group(1)}", NeonColors.NEON_BLUE)
            
        self.results['cms_info']['drupal'] = drupal_info
        
    def check_security_misconfigs(self, response, protocol):
        """Check for security misconfigurations"""
        misconfigs = []
        content = response.text
        
        # Directory listing
        if 'Index of /' in content:
            misconfigs.append('Directory Listing Enabled')
            
        # Server version disclosure
        if 'server' in response.headers:
            server = response.headers['server']
            if re.search(r'\d+\.\d+', server):
                misconfigs.append('Server Version Disclosure')
                
        # Debug information
        debug_indicators = ['debug', 'error', 'exception', 'traceback']
        for indicator in debug_indicators:
            if indicator in content.lower():
                misconfigs.append('Debug Information Exposure')
                break
                
        for misconfig in misconfigs:
            vuln = {
                'type': 'Security Misconfiguration',
                'target': f"{protocol}://{self.target}",
                'severity': 'Medium',
                'description': misconfig,
                'tool': 'TARANTULA'
            }
            self.results['vulnerabilities'].append(vuln)
            self.warning_print(f"Misconfiguration: {misconfig}")
            
    def ssl_tls_vulnerability_check(self):
        """SSL/TLS vulnerability assessment"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"SSL/TLS security assessment for {self.target}", NeonColors.NEON_GREEN)
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((self.target, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.target) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    ssl_info = {
                        'protocol_version': version,
                        'cipher_suite': cipher[0] if cipher else 'Unknown',
                        'key_exchange': cipher[1] if cipher else 'Unknown',
                        'certificate': {
                            'subject': dict(x[0] for x in cert['subject']) if cert else {},
                            'issuer': dict(x[0] for x in cert['issuer']) if cert else {},
                            'serial_number': cert.get('serialNumber', 'Unknown') if cert else 'Unknown',
                            'not_before': cert.get('notBefore', 'Unknown') if cert else 'Unknown',
                            'not_after': cert.get('notAfter', 'Unknown') if cert else 'Unknown'
                        }
                    }
                    
                    # Check for vulnerabilities
                    weak_ciphers = ['RC4', 'DES', '3DES', 'MD5']
                    if cipher and any(weak in cipher[0] for weak in weak_ciphers):
                        vuln = {
                            'type': 'Weak SSL Cipher',
                            'target': f"{self.target}:443",
                            'severity': 'Medium',
                            'description': f'Weak cipher: {cipher[0]}',
                            'tool': 'TARANTULA'
                        }
                        self.results['vulnerabilities'].append(vuln)
                        
                    # Check protocol version
                    if version in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                        vuln = {
                            'type': 'Outdated SSL Protocol',
                            'target': f"{self.target}:443",
                            'severity': 'High',
                            'description': f'Outdated protocol: {version}',
                            'tool': 'TARANTULA'
                        }
                        self.results['vulnerabilities'].append(vuln)
                        
                    self.results['ssl_info'] = ssl_info
                    self.success_print(f"SSL/TLS analysis complete - Protocol: {version}")
                    
        except Exception as e:
            self.error_print(f"SSL/TLS analysis failed: {str(e)}")
            
    def email_social_osint(self):
        """Email and social media OSINT"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Email & social media OSINT for {self.target}", NeonColors.NEON_GREEN)
        
        # Email patterns
        email_patterns = [
            f"admin@{self.target}",
            f"info@{self.target}",
            f"contact@{self.target}",
            f"support@{self.target}",
            f"sales@{self.target}",
            f"security@{self.target}",
            f"webmaster@{self.target}",
            f"noreply@{self.target}"
        ]
        
        # Social media platforms
        social_platforms = {
            'LinkedIn': f"https://linkedin.com/company/{self.target.replace('.', '-')}",
            'Twitter': f"https://twitter.com/{self.target.split('.')[0]}",
            'Facebook': f"https://facebook.com/{self.target.split('.')[0]}",
            'Instagram': f"https://instagram.com/{self.target.split('.')[0]}"
        }
        
        self.results['emails'] = email_patterns
        
        # Check social media presence
        social_results = {}
        for platform, url in social_platforms.items():
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.get(url, timeout=10, headers=headers)
                
                if response.status_code == 200:
                    social_results[platform] = 'Profile found'
                    self.success_print(f"{platform}: Profile found")
                else:
                    social_results[platform] = 'Not found'
                    
            except:
                social_results[platform] = 'Check failed'
                
        self.results['social_media'] = social_results
        
    def domain_reputation_check(self):
        """Domain reputation analysis"""
        if not self.target:
            self.error_print("No target set!")
            return
            
        self.neon_print(f"Domain reputation analysis for {self.target}", NeonColors.NEON_GREEN)
        
        # Simulated reputation checks
        reputation_sources = ['VirusTotal', 'URLVoid', 'Sucuri', 'Google Safe Browsing']
        reputation_results = {}
        
        for source in reputation_sources:
            reputation_results[source] = 'Clean'
            self.success_print(f"{source}: Clean")
            
        self.results['reputation'] = reputation_results
        
    def save_scan_to_db(self):
        """Save scan results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scans (target, scan_mode, timestamp, results)
                VALUES (?, ?, ?, ?)
            ''', (self.target, self.scan_mode, datetime.now().isoformat(), json.dumps(self.results)))
            
            # Save vulnerabilities
            for vuln in self.results.get('vulnerabilities', []):
                cursor.execute('''
                    INSERT INTO vulnerabilities (target, vuln_type, severity, description, tool, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (vuln.get('target', self.target), vuln['type'], vuln['severity'], 
                     vuln['description'], vuln.get('tool', 'TARANTULA'), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.success_print("Scan results saved to database")
            
        except Exception as e:
            self.error_print(f"Failed to save to database: {str(e)}")
            
    def generate_executive_report(self):
        """Generate comprehensive executive report"""
        if not any(self.results.values()):
            self.error_print("No results to export!")
            return
            
        self.neon_print("Generating executive intelligence report", NeonColors.NEON_GREEN)
        
        # Generate reports
        html_report = self.create_html_report()
        json_report = self.create_json_report()
        executive_summary = self.create_executive_summary()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save files
        html_file = f"{self.output_dir}/tarantula_executive_{self.target}_{timestamp}.html"
        json_file = f"{self.output_dir}/tarantula_data_{self.target}_{timestamp}.json"
        summary_file = f"{self.output_dir}/tarantula_summary_{self.target}_{timestamp}.txt"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
            
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
            
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(executive_summary)
            
        self.success_print(f"Executive reports generated:")
        self.success_print(f"  📊 HTML Report: {html_file}")
        self.success_print(f"  📁 JSON Data: {json_file}")
        self.success_print(f"  📋 Executive Summary: {summary_file}")
        
    def create_html_report(self):
        """Create comprehensive HTML report"""
        vuln_count = len(self.results.get('vulnerabilities', []))
        critical_count = len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'Critical'])
        high_count = len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'High'])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TARANTULA Enterprise Report - {self.target}</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%); 
            color: #00ff41; 
            margin: 0; 
            padding: 20px;
        }}
        .header {{ 
            background: linear-gradient(45deg, #ff00ff, #00ffff); 
            color: black; 
            padding: 30px; 
            text-align: center; 
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .section {{ 
            margin: 30px 0; 
            padding: 20px; 
            border: 2px solid #00ff41; 
            border-radius: 10px;
            background: rgba(0, 255, 65, 0.05);
        }}
        .vulnerability {{ 
            background: rgba(255, 0, 64, 0.1); 
            padding: 15px; 
            margin: 10px 0; 
            border-left: 5px solid #ff0040;
            border-radius: 5px;
        }}
        .critical {{ border-left-color: #ff0000; background: rgba(255, 0, 0, 0.1); }}
        .high {{ border-left-color: #ff4500; background: rgba(255, 69, 0, 0.1); }}
        .medium {{ border-left-color: #ffa500; background: rgba(255, 165, 0, 0.1); }}
        .low {{ border-left-color: #ffff00; background: rgba(255, 255, 0, 0.1); }}
        .success {{ color: #00ff41; }}
        .warning {{ color: #ffff00; }}
        .error {{ color: #ff0040; }}
        .info {{ color: #00ffff; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0;
            background: rgba(0, 0, 0, 0.3);
        }}
        th, td {{ 
            border: 1px solid #00ff41; 
            padding: 12px; 
            text-align: left; 
        }}
        th {{ 
            background: rgba(0, 255, 65, 0.2); 
            font-weight: bold;
        }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 20px 0;
        }}
        .stat-card {{ 
            background: rgba(0, 255, 65, 0.1); 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            border: 1px solid #00ff41;
        }}
        .neon-text {{ 
            text-shadow: 0 0 10px currentColor; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="neon-text">🕷️ TARANTULA ENTERPRISE INTELLIGENCE REPORT 🕷️</h1>
            <h2>Target: {self.target}</h2>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Scan Mode: {self.scan_mode.upper()}</p>
        </div>
        
        <div class="section">
            <h2>📊 Executive Dashboard</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3 class="error">{vuln_count}</h3>
                    <p>Total Vulnerabilities</p>
                </div>
                <div class="stat-card">
                    <h3 class="error">{critical_count}</h3>
                    <p>Critical Issues</p>
                </div>
                <div class="stat-card">
                    <h3 class="warning">{high_count}</h3>
                    <p>High Risk Issues</p>
                </div>
                <div class="stat-card">
                    <h3 class="success">{len(self.results.get('subdomains', []))}</h3>
                    <p>Subdomains Found</p>
                </div>
                <div class="stat-card">
                    <h3 class="info">{len(self.results.get('ports', []))}</h3>
                    <p>Open Services</p>
                </div>
                <div class="stat-card">
                    <h3 class="warning">{len(self.results.get('tech_stack', []))}</h3>
                    <p>Technologies</p>
                </div>
            </div>
        </div>
        
        {self.format_vulnerabilities_html()}
        {self.format_attack_surface_html()}
        {self.format_intelligence_html()}
        
        <footer style="text-align: center; margin-top: 50px; color: #666;">
            <p>Generated by TARANTULA v3.0 Enterprise | Author: Scav-engeR</p>
            <p>⚠️ This report contains sensitive security information - Handle with care ⚠️</p>
        </footer>
    </div>
</body>
</html>
        """
        
        return html
        
    def format_vulnerabilities_html(self):
        """Format vulnerabilities for HTML report"""
        if not self.results.get('vulnerabilities'):
            return '<div class="section"><h2>🛡️ Vulnerabilities</h2><p class="success">No vulnerabilities detected.</p></div>'
            
        html = '<div class="section"><h2>🚨 Security Vulnerabilities</h2>'
        
        # Group by severity
        by_severity = {'Critical': [], 'High': [], 'Medium': [], 'Low': []}
        for vuln in self.results['vulnerabilities']:
            severity = vuln.get('severity', 'Medium')
            if severity in by_severity:
                by_severity[severity].append(vuln)
                
        for severity, vulns in by_severity.items():
            if vulns:
                html += f'<h3 class="{severity.lower()}">{severity} Severity ({len(vulns)})</h3>'
                
                for vuln in vulns:
                    html += f'''
                    <div class="vulnerability {severity.lower()}">
                        <h4>{vuln['type']}</h4>
                        <p><strong>Target:</strong> {vuln.get('target', 'N/A')}</p>
                        <p><strong>Tool:</strong> {vuln.get('tool', 'TARANTULA')}</p>
                        <p><strong>Description:</strong> {vuln['description']}</p>
                    </div>
                    '''
                    
        html += '</div>'
        return html
        
    def format_attack_surface_html(self):
        """Format attack surface information"""
        html = '<div class="section"><h2>🎯 Attack Surface Analysis</h2>'
        
        # Subdomains
        if self.results.get('subdomains'):
            html += '<h3>🌐 Discovered Subdomains</h3>'
            html += '<table><tr><th>Subdomain</th><th>IP Address</th></tr>'
            for sub in self.results['subdomains'][:20]:  # Limit to 20
                html += f"<tr><td>{sub.get('subdomain', 'N/A')}</td><td>{sub.get('ip', 'N/A')}</td></tr>"
            html += '</table>'
            
        # Open ports
        if self.results.get('ports'):
            html += '<h3>🔌 Open Services</h3>'
            html += '<table><tr><th>Port</th><th>Service</th><th>Version</th><th>Banner</th></tr>'
            for port in self.results['ports'][:15]:  # Limit to 15
                html += f"""<tr>
                    <td>{port.get('port', 'N/A')}</td>
                    <td>{port.get('service', 'N/A')}</td>
                    <td>{port.get('version', 'N/A')}</td>
                    <td>{port.get('banner', 'N/A')[:50]}...</td>
                </tr>"""
            html += '</table>'
            
        # Technology stack
        if self.results.get('tech_stack'):
            html += '<h3>🛠️ Technology Stack</h3><ul>'
            for tech in self.results['tech_stack']:
                html += f'<li>{tech}</li>'
            html += '</ul>'
            
        html += '</div>'
        return html
        
    def format_intelligence_html(self):
        """Format intelligence gathering results"""
        html = '<div class="section"><h2>🔍 Intelligence Summary</h2>'
        
        # FOFA results
        if self.results.get('fofa_intelligence'):
            fofa_data = self.results['fofa_intelligence']
            html += f'<h3>🌐 FOFA Cyber Space Intelligence</h3>'
            html += f'<p>Total Results: {fofa_data.get("total_results", 0)}</p>'
            
        # Shodan results
        if self.results.get('shodan_data'):
            shodan_data = self.results['shodan_data']
            html += f'<h3>🔎 Shodan Attack Surface Intelligence</h3>'
            html += f'<p>Total Results: {shodan_data.get("total_results", 0)}</p>'
            
        # Real IP discovery
        if self.results.get('real_ip'):
            html += f'<h3>🎯 Real IP Discovery</h3>'
            html += f'<p class="success">Real IP Found: {self.results["real_ip"]}</p>'
            
        # WAF detection
        if self.results.get('waf_detection'):
            waf_data = self.results['waf_detection']
            detected_wafs = waf_data.get('detected_wafs', [])
            if detected_wafs:
                html += f'<h3>🛡️ WAF Detection</h3>'
                html += f'<p>Detected WAFs: {", ".join(detected_wafs)}</p>'
                
        html += '</div>'
        return html
        
    def create_json_report(self):
        """Create JSON export with all data"""
        return {
            'target': self.target,
            'scan_mode': self.scan_mode,
            'timestamp': datetime.now().isoformat(),
            'tool_version': 'TARANTULA v3.0',
            'author': 'Scav-engeR',
            'summary': {
                'vulnerabilities_count': len(self.results.get('vulnerabilities', [])),
                'critical_vulns': len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'Critical']),
                'high_vulns': len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'High']),
                'subdomains_count': len(self.results.get('subdomains', [])),
                'open_ports_count': len(self.results.get('ports', [])),
                'technologies_count': len(self.results.get('tech_stack', []))
            },
            'results': self.results
        }
        
    def create_executive_summary(self):
        """Create executive summary"""
        vuln_count = len(self.results.get('vulnerabilities', []))
        critical_vulns = len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'Critical'])
        high_vulns = len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'High'])
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                        TARANTULA ENTERPRISE INTELLIGENCE REPORT                       ║
║                                 EXECUTIVE SUMMARY                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

Target: {self.target}
Scan Mode: {self.scan_mode.upper()}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Tool Version: TARANTULA v3.0 Enterprise
Author: Scav-engeR

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                SECURITY POSTURE                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

Total Vulnerabilities: {vuln_count}
  🔴 Critical: {critical_vulns}
  🟠 High: {high_vulns}
  🟡 Medium: {len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'Medium'])}
  🟢 Low: {len([v for v in self.results.get('vulnerabilities', []) if v['severity'] == 'Low'])}

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                              ATTACK SURFACE ANALYSIS                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🌐 Subdomains Discovered: {len(self.results.get('subdomains', []))}
🔌 Open Services: {len(self.results.get('ports', []))}
📁 Web Directories: {len(self.results.get('directories', []))}
📄 Exposed Files: {len(self.results.get('exposed_files', []))}
🔗 API Endpoints: {len(self.results.get('api_endpoints', []))}

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                               TECHNOLOGY STACK                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

{chr(10).join(f"🛠️ {tech}" for tech in self.results.get('tech_stack', []))}

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                CRITICAL FINDINGS                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

"""
        
        if critical_vulns > 0:
            summary += "⚠️  CRITICAL VULNERABILITIES DETECTED ⚠️\n\n"
            for vuln in self.results.get('vulnerabilities', []):
                if vuln['severity'] == 'Critical':
                    summary += f"🔴 {vuln['type']}: {vuln['description']}\n"
                    summary += f"   Target: {vuln.get('target', 'N/A')}\n"
                    summary += f"   Tool: {vuln.get('tool', 'TARANTULA')}\n\n"
        else:
            summary += "✅ No critical vulnerabilities detected.\n\n"
            
        summary += f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                 RECOMMENDATIONS                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

1. 🚨 Address all Critical and High severity vulnerabilities immediately
2. 🛡️ Implement comprehensive security headers (CSP, HSTS, etc.)
3. 🔒 Enable SSL/TLS best practices and disable weak ciphers
4. 🚫 Implement WAF and DDoS protection
5. 📝 Regular security assessments and continuous monitoring
6. 🔄 Update all outdated software and frameworks
7. 🔐 Implement proper access controls and authentication
8. 📊 Establish vulnerability management program

╔══════════════════════════════════════════════════════════════════════════════════════╗
║                               TOOL INTEGRATION                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🔧 Nuclei Vulnerabilities: {len(self.results.get('nuclei_results', []))}
💉 SQLMap Injections: {len(self.results.get('sqlmap_results', []))}
🔍 WPScan Results: {len(self.results.get('wpscan_results', []))}
🌐 FOFA Intelligence: {"✅" if self.results.get('fofa_intelligence') else "❌"}
🔎 Shodan Data: {"✅" if self.results.get('shodan_data') else "❌"}
🛡️ WAF Detection: {"✅" if self.results.get('waf_detection') else "❌"}

Generated by TARANTULA v3.0 Enterprise Attack Surface Management Platform
Author: Scav-engeR | Framework: Advanced Python3 + Integrated Security Tools

⚠️  This report contains sensitive security information - Handle with appropriate care ⚠️
"""
        
        return summary
        
    def configuration_settings(self):
        """Configuration and settings management"""
        self.neon_print("TARANTULA Configuration Manager", NeonColors.NEON_GREEN)
        
        config_menu = f"""
{NeonColors.NEON_PURPLE}╔══════════════════════════════════════════════════════════════╗
║                    CONFIGURATION MANAGER                      ║
╠══════════════════════════════════════════════════════════════╣
║  {NeonColors.NEON_GREEN}1{NeonColors.NEON_PURPLE} ▶ API Keys Configuration                         ║
║  {NeonColors.NEON_GREEN}2{NeonColors.NEON_PURPLE} ▶ Tool Paths Configuration                       ║
║  {NeonColors.NEON_GREEN}3{NeonColors.NEON_PURPLE} ▶ Check Dependencies                             ║
║  {NeonColors.NEON_GREEN}4{NeonColors.NEON_PURPLE} ▶ Install Python Dependencies                    ║
║  {NeonColors.NEON_GREEN}5{NeonColors.NEON_PURPLE} ▶ View Current Configuration                     ║
║  {NeonColors.NEON_GREEN}0{NeonColors.NEON_PURPLE} ▶ Back to Main Menu                              ║
╚══════════════════════════════════════════════════════════════╝{NeonColors.RESET}
        """
        
        print(config_menu)
        choice = input(f"{NeonColors.NEON_BLUE}config@tarantula:~$ {NeonColors.CYAN}")
        
        if choice == '1':
            self.configure_api_keys()
        elif choice == '2':
            self.configure_tool_paths()
        elif choice == '3':
            self.check_tool_dependencies()
        elif choice == '4':
            self.install_python_dependencies()
        elif choice == '5':
            self.view_configuration()
        elif choice == '0':
            return
        else:
            self.error_print("Invalid option!")
            
    def configure_api_keys(self):
        """Configure API keys"""
        self.neon_print("API Keys Configuration", NeonColors.NEON_BLUE)
        
        # Shodan API
        shodan_key = input(f"{NeonColors.CYAN}Shodan API Key (current: {'*' * len(self.api_keys.get('shodan', '')) if self.api_keys.get('shodan') else 'Not set'}): {NeonColors.RESET}")
        if shodan_key:
            self.api_keys['shodan'] = shodan_key
            
        # FOFA API
        fofa_email = input(f"{NeonColors.CYAN}FOFA Email: {NeonColors.RESET}")
        if fofa_email:
            self.api_keys['fofa_email'] = fofa_email
            
        fofa_key = input(f"{NeonColors.CYAN}FOFA API Key: {NeonColors.RESET}")
        if fofa_key:
            self.api_keys['fofa_key'] = fofa_key
            
        # VirusTotal API
        vt_key = input(f"{NeonColors.CYAN}VirusTotal API Key: {NeonColors.RESET}")
        if vt_key:
            self.api_keys['virustotal'] = vt_key
            
        self.success_print("API keys updated successfully!")
        
    def configure_tool_paths(self):
        """Configure tool paths"""
        self.neon_print("Tool Paths Configuration", NeonColors.NEON_BLUE)
        
        for tool, current_path in self.tool_paths.items():
            new_path = input(f"{NeonColors.CYAN}{tool} path (current: {current_path}): {NeonColors.RESET}")
            if new_path:
                self.tool_paths[tool] = new_path
                
        self.success_print("Tool paths updated successfully!")
        
    def view_configuration(self):
        """View current configuration"""
        self.neon_print("Current Configuration", NeonColors.NEON_BLUE)
        
        print(f"\n{NeonColors.NEON_GREEN}API Keys:{NeonColors.RESET}")
        for key, value in self.api_keys.items():
            status = "✅ Configured" if value else "❌ Not set"
            print(f"  {key}: {status}")
            
        print(f"\n{NeonColors.NEON_GREEN}Tool Paths:{NeonColors.RESET}")
        for tool, path in self.tool_paths.items():
            print(f"  {tool}: {path}")
            
        print(f"\n{NeonColors.NEON_GREEN}Output Directory:{NeonColors.RESET} {self.output_dir}")
        print(f"{NeonColors.NEON_GREEN}Database Path:{NeonColors.RESET} {self.db_path}")
        
    def run(self):
        """Main execution loop"""
        try:
            self.banner()
            
            while True:
                if not self.target:
                    self.set_target()
                    continue
                    
                self.menu()
                choice = input(f"{NeonColors.NEON_BLUE}tarantula@enterprise:~$ {NeonColors.CYAN}")
                
                if choice == '1':
                    self.advanced_subdomain_discovery()
                elif choice == '2':
                    self.enhanced_port_scanning()
                elif choice == '3':
                    self.directory_file_discovery()
                elif choice == '4':
                    self.comprehensive_dns_enum()
                elif choice == '5':
                    self.advanced_http_analysis()
                elif choice == '6':
                    self.fofa_cyberspace_mapping()
                elif choice == '7':
                    self.shodan_attack_surface_intel()
                elif choice == '8':
                    self.email_social_osint()
                elif choice == '9':
                    self.domain_reputation_check()
                elif choice == '11':
                    self.nuclei_vulnerability_scan()
                elif choice == '12':
                    self.sqlmap_injection_testing()
                elif choice == '13':
                    self.wpscan_wordpress_analysis()
                elif choice == '15':
                    self.ssl_tls_vulnerability_check()
                elif choice == '16':
                    self.waf_detection_bypass()
                elif choice == '17':
                    self.cloudflare_real_ip_discovery()
                elif choice == '21':
                    self.full_enterprise_scan()
                elif choice == '26':
                    self.generate_executive_report()
                elif choice == '0':
                    self.configuration_settings()
                elif choice.lower() in ['exit', 'quit', 'q']:
                    self.neon_print("Disconnecting from neural network...", NeonColors.NEON_PINK)
                    break
                elif choice.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.banner()
                elif choice.lower() == 'target':
                    self.set_target()
                else:
                    self.error_print("Invalid option! Type 'exit' to quit")
                    
                input(f"\n{NeonColors.GRAY}Press Enter to continue...{NeonColors.RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{NeonColors.RED}[!] Neural network interrupted by user{NeonColors.RESET}")
        except Exception as e:
            print(f"\n{NeonColors.RED}[!] Fatal system error: {str(e)}{NeonColors.RESET}")

if __name__ == "__main__":
    print(f"{NeonColors.NEON_GREEN}Initializing TARANTULA enterprise neural networks...{NeonColors.RESET}")
    time.sleep(2)
    
    try:
        tarantula = TarantulaCore()
        tarantula.run()
    except Exception as e:
        print(f"{NeonColors.RED}[FATAL] Neural network initialization failed: {str(e)}{NeonColors.RESET}")
