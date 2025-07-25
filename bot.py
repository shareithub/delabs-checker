import requests
import json
import time
import os
import shareithub
from shareithub import shareithub
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

console = Console()

URL = 'https://airdrop.delabs.gg/'
ADDRESS_FILE = 'address.txt'
DELAY_PER_ACCOUNT = 10  

HEADERS = {
    'accept': 'text/x-component',
    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
    'content-type': 'text/plain;charset=UTF-8',
    'next-action': '400bed965031ea7815d60516d4e4225590783ff093',
    'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22(home)%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2F%22%2C%22refresh%22%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
    'origin': 'https://airdrop.delabs.gg',
    'priority': 'u=1, i',
    'referer': 'https://airdrop.delabs.gg/',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
}

COOKIES_TEMPLATE = {
    '__cf_bm': 'tWV1KeNitXOKo3dwSz7Vp46VJn7Bt9zkdZ2v5GN6R_Y-1753459493-1.0.1.1-7cH1uDk91T_MTgDLT.Tt9hn_d02FukjfDzIUZb4iUef0fBgRwWo0K0hxlD_sg2h0U6m9K.ec.aZu7BmhKJBgdlnvf249x3M2qtOOIJeri3E',
    '_cfuvid': 'HrpsMyK1yJ_7RzRhOZOY6QhuayOT.sGoXlrXSZk7Ok4-1753459493050-0.0.1.1-604800000',
    'AWSALB': 'ZVddY7CMJOHbZlS/p6SRpCMS7l4TODCJHChNyVFI0Nu5eZ+7X3TkDCZhw26A13Sy894sgTKuKqyAMDA6Xqb1QdeEU5XdUMQchl8p/rvUF19jGgIFDGPQ56QMKCAd',
    'AWSALBCORS': 'ZVddY7CMJOHbZlS/p6SRpCMS7l4TODCJHChNyVFI0Nu5eZ+7X3TkDCZhw26A13Sy894sgTKuKqyAMDA6Xqb1QdeEU5XdUMQchl8p/rvUF19jGgIFDGPQ56QMKCAd',
    'wagmi.recentConnectorId': '"com.okex.wallet"',
}

WAGMI_STORE_TEMPLATE = {
    "state": {"connections": {"__type": "Map", "value": [["6e94737e6f5", {"accounts": ["0xC0fb98545d21D991d62b4fae5Ad4d478259a617A"],"chainId": 1,"connector": {"id": "com.okex.wallet","name": "OKX Wallet","type": "injected","uid": "6e94737e6f5"}}]]},"chainId": 1,"current": "6e94737e6f5"},"version": 2
}

def load_addresses():
    """Membaca alamat dari file address.txt."""
    if not os.path.exists(ADDRESS_FILE):
        console.print(f"[bold red]Error: File '{ADDRESS_FILE}' tidak ditemukan![/bold red]")
        return None
    with open(ADDRESS_FILE, 'r') as f:
        addresses = [line.strip() for line in f if line.strip()]
    if not addresses:
        console.print(f"[bold yellow]Warning: File '{ADDRESS_FILE}' kosong.[/bold yellow]")
        return None
    return addresses

def process_account(address: str):
    """Membuat dan mengirim permintaan untuk satu alamat."""
    try:

        payload_data = [{"evmWalletAddress": address}]
        payload = json.dumps(payload_data)

        current_cookies = COOKIES_TEMPLATE.copy()
        wagmi_store_dynamic = WAGMI_STORE_TEMPLATE.copy()
        wagmi_store_dynamic["state"]["connections"]["value"][0][1]["accounts"] = [address]
        current_cookies['wagmi.store'] = json.dumps(wagmi_store_dynamic, separators=(',', ':'))

        response = requests.post(URL, headers=HEADERS, cookies=current_cookies, data=payload, timeout=15)

        status_code = response.status_code
        response_text = response.text

        if status_code == 200:
            if '"status":"notEligible"' in response_text:
                status_emoji = "❌"
                status_text = "[bold red]TIDAK ELIGIBLE[/bold red]"
                
                display_panel = Panel(
                    Text("\nAkun ini tidak eligible untuk airdrop.\n", justify="center"),
                    title="[bold red]❌ Status: Tidak Memenuhi Syarat ❌[/bold red]",
                    border_style="red",
                    expand=False
                )
                return status_emoji, status_text, display_panel
            else:
                status_emoji = "✅"
                status_text = f"[bold green]OK ({status_code})[/bold green]"
                return status_emoji, status_text, ' '.join(response_text.split())
        else:
            status_emoji = "❌"
            status_text = f"[bold red]FAIL ({status_code})[/bold red]"
            return status_emoji, status_text, response_text

    except requests.exceptions.RequestException as e:
        return "❌", "[bold red]NETWORK ERROR[/bold red]", str(e)
    except Exception as e:
        return "❌", "[bold red]SCRIPT ERROR[/bold red]", str(e)

def main():
    """Fungsi utama untuk menjalankan bot."""
    console.print(Panel("[bold cyan]🚀 Delabs Airdrop Bot by Gemini 🚀[/bold cyan]", 
                        title="[yellow]Start[/yellow]", subtitle="[green]v1.1[/green]"))

    addresses = load_addresses()
    if not addresses:
        return

    table = Table(title="📊 Hasil Proses Akun")
    table.add_column("No.", justify="center", style="cyan")
    table.add_column("Alamat Wallet", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Respons Server") 

    total_accounts = len(addresses)
    console.log(f"[bold]Memulai proses untuk {total_accounts} akun...[/bold]")

    with Live(table, refresh_per_second=4, console=console) as live:
        for i, address in enumerate(addresses, 1):
            live.console.log(f"Memproses Akun {i}/{total_accounts}: [cyan]{address[:10]}...{address[-4:]}[/cyan]")
            
            emoji, status, response_data = process_account(address)
            
            table.add_row(f"{emoji} {i}", address, status, response_data)
            
            if i < total_accounts:
                live.console.log(f"Menunggu {DELAY_PER_ACCOUNT} detik sebelum lanjut...")
                time.sleep(DELAY_PER_ACCOUNT)
    
    console.print(Panel("[bold green]✅ Proses Selesai Semua Akun! ✅[/bold green]"))

if __name__ == "__main__":
    main()
