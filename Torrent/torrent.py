import streamlit as st
import libtorrent as lt
import time
import os
from datetime import datetime

class TorrentEngine:
    """Classe responsável pela lógica de baixo nível do libtorrent."""
    
    def __init__(self, download_path, max_connections=1000):
        self.ses = lt.session()
        self.download_path = download_path
        self._configure_session(max_connections)

    def _configure_session(self, max_connections):
        settings = self.ses.get_settings()
        settings.update({
            'connections_limit': max_connections,
            'active_downloads': 10,
            'connection_speed': 500,
            'peer_connect_timeout': 2,
            'announce_ip': "0.0.0.0"
        })
        self.ses.apply_settings(settings)
        # Habilita DHT e UPnP para maximizar conexões
        self.ses.add_extension('ut_metadata')
        self.ses.add_extension('ut_pex')
        self.ses.start_dht()

    def add_torrent(self, torrent_content):
        with open("temp.torrent", "wb") as f:
            f.write(torrent_content)
        
        info = lt.torrent_info("temp.torrent")
        params = {
            'save_path': self.download_path,
            'ti': info,
            'storage_mode': lt.storage_mode_t.storage_mode_sparse
        }
        return self.ses.add_torrent(params), info

# --- Interface Streamlit ---

def render_sidebar():
    st.sidebar.header("⚙️ Configurações Técnicas")
    max_conns = st.sidebar.slider("Limite de Conexões", 100, 2000, 1000, step=100)
    path = st.sidebar.text_input("Diretório de Download", value=os.path.join(os.getcwd(), "downloads"))
    return max_conns, path

def display_metrics(status):
    cols = st.columns(4)
    cols[0].metric("Progresso", f"{status.progress * 100:.1f}%")
    cols[1].metric("Download", f"{status.download_rate / 1000:.1f} kB/s")
    cols[2].metric("Upload", f"{status.upload_rate / 1000:.1f} kB/s")
    cols[3].metric("Peers/Seeds", f"{status.num_peers} ({status.num_seeds})")

def main():
    st.set_page_config(page_title="Torrent PO Client", layout="wide")
    st.title("📥 Torrent Client: Alta Performance")
    
    max_conns, path = render_sidebar()
    
    # Inicialização da engine no estado da sessão
    if 'engine' not in st.session_state:
        st.session_state.engine = TorrentEngine(path, max_conns)
        st.session_state.history = []

    uploaded_file = st.file_uploader("Selecione o arquivo .torrent", type=['torrent'])

    if uploaded_file:
        handle, info = st.session_state.engine.add_torrent(uploaded_file.getbuffer())
        
        st.subheader(f"📦 {info.name()}")
        
        # Containers de UI para atualização dinâmica
        prog_bar = st.progress(0)
        metrics_area = st.empty()
        chart_area = st.empty()

        while not handle.is_seed():
            s = handle.status()
            
            # Atualiza UI
            prog_bar.progress(s.progress)
            
            with metrics_area.container():
                display_metrics(s)
            
            # Gráfico de velocidade
            st.session_state.history.append(s.download_rate / 1000)
            if len(st.session_state.history) > 60: st.session_state.history.pop(0)
            chart_area.line_chart(st.session_state.history, height=200)
            
            if s.state == lt.torrent_status.seeding:
                st.success("Download Concluído! Semeando...")
                break
                
            time.sleep(1)

if __name__ == "__main__":
    main()