// Relaciona nombres de equipos con sus escudos para la interfaz de partidos.
const teamBadgeMap = {
  // La Liga (Spain)
  'real madrid': 'IMG/Real Madrid.jpg',
  'barcelona': 'IMG/Barcelona.jpg',
  'atlético de madrid': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0b/Atletico_Madrid_2012.svg/330px-Atletico_Madrid_2012.svg.png',
  'valencia': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/Valencia_CF.svg/330px-Valencia_CF.svg.png',
  'sevilla': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Sevilla_FC.svg/330px-Sevilla_FC.svg.png',
  'girona': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c4/Girona_FC.svg/330px-Girona_FC.svg.png',
  'athletic club': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6a/Athletic_Bilbao.svg/330px-Athletic_Bilbao.svg.png',
  'real betis': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/12/Real_Betis.svg/330px-Real_Betis.svg.png',
  'rcd espanyol': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/RCD_Espanyol.svg/330px-RCD_Espanyol.svg.png',
  'villarreal': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7c/Villarreal_CF.svg/330px-Villarreal_CF.svg.png',
  
  // Premier League (England)
  'manchester united': 'IMG/ManchesterU.jpg',
  'manchester city': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/330px-Manchester_City_FC_badge.svg.png',
  'arsenal': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/330px-Arsenal_FC.svg.png',
  'liverpool': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/330px-Liverpool_FC.svg.png',
  'chelsea': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/330px-Chelsea_FC.svg.png',
  'tottenham': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Tottenham_Hotspur.svg/330px-Tottenham_Hotspur.svg.png',
  'brighton': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Brighton_and_Hove_Albion_FC_logo.svg/330px-Brighton_and_Hove_Albion_FC_logo.svg.png',
  'aston villa': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Aston_Villa_FC_Crest.svg/330px-Aston_Villa_FC_Crest.svg.png',
  'newcastle': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Newcastle_United_Logo.svg/330px-Newcastle_United_Logo.svg.png',
  'bournemouth': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/AFC_Bournemouth_%282013%29.svg/330px-AFC_Bournemouth_%282013%29.svg.png',
  'everton': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7c/Everton_FC_logo.svg/330px-Everton_FC_logo.svg.png',
  'crystal palace': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Crystal_Palace_FC_logo.svg/330px-Crystal_Palace_FC_logo.svg.png',
  'fulham': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Fulham_FC_%282018%29.svg/330px-Fulham_FC_%282018%29.svg.png',
  'brentford': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Brentford_FC_%28current%29.svg/330px-Brentford_FC_%28current%29.svg.png',
  'luton': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/88/Luton_Town_FC.svg/330px-Luton_Town_FC.svg.png',
  'ipswich': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/Ipswich_Town_FC_logo.svg/330px-Ipswich_Town_FC_logo.svg.png',
  'wolverhampton': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/fc/Wolverhampton_Wanderers_FC.svg/330px-Wolverhampton_Wanderers_FC.svg.png',
  'west ham': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/West_Ham_United_FC_logo.svg/330px-West_Ham_United_FC_logo.svg.png',
  'nottingham': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/Nottingham_Forest_FC_logo.svg/330px-Nottingham_Forest_FC_logo.svg.png',
  'southampton': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/FC_Southampton.svg/330px-FC_Southampton.svg.png',
  'leicester': 'https://upload.wikimedia.org/wikipedia/en/thumb/2/2d/Leicester_City_FC_logo.svg/330px-Leicester_City_FC_logo.svg.png',
  
  // Serie A (Italy)
  'juventus': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/05/Juventus_FC_2023_logo.svg/330px-Juventus_FC_2023_logo.svg.png',
  'inter': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/05/Inter_Milan.svg/330px-Inter_Milan.svg.png',
  'milan': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d0/AC_Milan.svg/330px-AC_Milan.svg.png',
  'napoli': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0f/S.S.C._Napoli_logo.svg/330px-S.S.C._Napoli_logo.svg.png',
  'roma': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/AS_Roma_2017_logo.svg/330px-AS_Roma_2017_logo.svg.png',
  'lazio': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/SS_Lazio.svg/330px-SS_Lazio.svg.png',
  'atalanta': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7f/Atalanta_BC.svg/330px-Atalanta_BC.svg.png',
  'fiorentina': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/45/ACF_Fiorentina_2022.svg/330px-ACF_Fiorentina_2022.svg.png',
  'torino': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e9/Torino_FC_logo.svg/330px-Torino_FC_logo.svg.png',
  'bologna': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/FC_Bologna_2012-14.svg/330px-FC_Bologna_2012-14.svg.png',
  'genoa': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/75/Genoa_CFC.svg/330px-Genoa_CFC.svg.png',
  'cagliari': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/76/Cagliari_Calcio_logo.svg/330px-Cagliari_Calcio_logo.svg.png',
  'udinese': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/16/Udinese_Calcio.svg/330px-Udinese_Calcio.svg.png',
  'venezia': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/Venezia_FC_logo.svg/330px-Venezia_FC_logo.svg.png',
  'frosinone': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/4f/Frosinone_Calcio_2021.svg/330px-Frosinone_Calcio_2021.svg.png',
  
  // Liga BetPlay Dimayor (Colombia)
  'millonarios': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/54/Millonarios_FC_%282018%29.svg/330px-Millonarios_FC_%282018%29.svg.png',
  'junior': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Junior_de_Barranquilla.svg/330px-Junior_de_Barranquilla.svg.png',
  'atlético nacional': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/Atlético_Nacional.svg/330px-Atlético_Nacional.svg.png',
  'santa fe': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d4/Santa_Fe_logo_2018.svg/330px-Santa_Fe_logo_2018.svg.png',
  'pasto': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/57/Deportivo_Pasto_logo.svg/330px-Deportivo_Pasto_logo.svg.png',
  'tolima': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/96/Deportes_Tolima_logo_%282017%29.svg/330px-Deportes_Tolima_logo_%282017%29.svg.png',
  'américa de cali': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c8/América_de_Cali.svg/330px-América_de_Cali.svg.png',
  'alianza petrolera': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/14/Alianza_Petrolera.svg/330px-Alianza_Petrolera.svg.png',
  'nacional': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/Atlético_Nacional.svg/330px-Atlético_Nacional.svg.png',
  'boyacá chicó': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f3/Boyaca_Chico_FC.svg/330px-Boyaca_Chico_FC.svg.png',
  'cúcuta deportivo': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/86/Cúcuta_Deportivo.svg/330px-Cúcuta_Deportivo.svg.png',
  
  // Champions League & European
  'bayern munich': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/1f/FC_Bayern_Munich_logo_%282017%29.svg/330px-FC_Bayern_Munich_logo_%282017%29.svg.png',
  'psg': 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Paris_Saint-Germain_F.C..svg/330px-Paris_Saint-Germain_F.C..svg.png',
  'paris saint-germain': 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Paris_Saint-Germain_F.C..svg/330px-Paris_Saint-Germain_F.C..svg.png',
  'bayer leverkusen': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e2/Bayer_Leverkusen_logo.svg/330px-Bayer_Leverkusen_logo.svg.png',
  'borussia dortmund': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/63/Borussia_Dortmund_logo.svg/330px-Borussia_Dortmund_logo.svg.png',
  'manchester city': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/330px-Manchester_City_FC_badge.svg.png',
  
  // CONMEBOL Libertadores (South America)
  'mirassol sp': 'https://upload.wikimedia.org/wikipedia/pt/thumb/1/16/Mirassol_Futebol_Clube_logo.svg/330px-Mirassol_Futebol_Clube_logo.svg.png',
  'ldu quito': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Liga_Deportiva_Universitaria_de_Quito.svg/330px-Liga_Deportiva_Universitaria_de_Quito.svg.png',
  'rosario central': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/52/Rosario_Central_Logo.svg/330px-Rosario_Central_Logo.svg.png',
  'corinthians': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/Sport_Club_Corinthians_Paulista.svg/330px-Sport_Club_Corinthians_Paulista.svg.png',
  
  // UEFA Europa League
  'cs u craiova': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/01/CSU_Craiova.svg/330px-CSU_Craiova.svg.png',
  'kuopion palloseura': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d7/KuPS_FC_logo.svg/330px-KuPS_FC_logo.svg.png',
  'ac omonia nicosia': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7d/AC_Omonia.svg/330px-AC_Omonia.svg.png',
  'lincoln red imps fc': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d1/Lincoln_Red_Imps_FC_logo.svg/330px-Lincoln_Red_Imps_FC_logo.svg.png',
  'gornik zabrze': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c6/Gornik_Zabrze_logo.svg/330px-Gornik_Zabrze_logo.svg.png',
  'ferencvarosi tc': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/Ferencváros_TC.svg/330px-Ferencváros_TC.svg.png',
  'besiktas': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/Beşiktaş_JK.svg/330px-Beşiktaş_JK.svg.png',
  'fc hradec kralove': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/33/FC_Hradec_Králové.svg/330px-FC_Hradec_Králové.svg.png',
  'pafos fc': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/73/Pafos_FC_logo.svg/330px-Pafos_FC_logo.svg.png',
  'rb salzburg': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d9/FC_Red_Bull_Salzburg.svg/330px-FC_Red_Bull_Salzburg.svg.png',
  'ki klaksvik': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/KÍ_Klaksvik.svg/330px-KÍ_Klaksvik.svg.png',
  'lech poznan': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e8/Lech_Poznań.svg/330px-Lech_Poznań.svg.png',
  'vikingur reykjavik': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7f/Vikingur_Reykjavík.svg/330px-Vikingur_Reykjavík.svg.png',
  'thun': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0f/FC_Thun.svg/330px-FC_Thun.svg.png',
  'cska sofia': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6e/PFC_CSKA_Sofia.svg/330px-PFC_CSKA_Sofia.svg.png',
  'maccabi tel aviv fc': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/61/Maccabi_Tel_Aviv_FC.svg/330px-Maccabi_Tel_Aviv_FC.svg.png',
  'rsc anderlecht': 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a1/RSC_Anderlecht.svg/330px-RSC_Anderlecht.svg.png',
  'paok tesalonica': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/PAOK_FC.svg/330px-PAOK_FC.svg.png',
  'glasgow rangers': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Rangers_FC.svg/330px-Rangers_FC.svg.png',
  'jagiellonia bialystok': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/Jagiellonia_Białystok.svg/330px-Jagiellonia_Białystok.svg.png',
  'heart of midlothian fc': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Heart_of_Midlothian_FC_logo.svg/330px-Heart_of_Midlothian_FC_logo.svg.png',
  'benfica': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/ee/SL_Benfica.svg/330px-SL_Benfica.svg.png',
  'egnatia': 'https://upload.wikimedia.org/wikipedia/en/thumb/2/2f/KF_Egnatia.svg/330px-KF_Egnatia.svg.png',
  'shamrock rovers fc': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Shamrock_Rovers_FC_logo.svg/330px-Shamrock_Rovers_FC_logo.svg.png'
};

// Busca el escudo de un equipo y usa un valor genérico si no existe.
function getTeamBadge(teamName){
  if (!teamName) return null;
  const key = teamName.toLowerCase().trim();
  return teamBadgeMap[key] || null;
}

// Construye el marcado HTML del escudo mostrado junto al equipo.
function getBadgeMarkup(teamName, side = 'home'){
  // No mostrar badges - solo retornar cadena vacía
  return '';
}

async function fetchPartidos(){
  try{
    const res = await fetch('/api/partidos', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Fetch response status:', res.status);
    
    if(!res.ok) {
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log('Received data:', data);
    
    if(!data) {
      throw new Error('No data returned from API');
    }
    
    const leagues = data.leagues || [];
    const featured = data.featured || [];
    
    console.log('Leagues:', leagues.length, 'Featured:', featured.length);
    
    renderLeagues(leagues);
    // renderFeatured deshabilitado - solo mostrar partidos principales
    
  }catch(err){
    console.error('Error in fetchPartidos:', err);
    document.getElementById('leaguesList').innerHTML = '<p class="text-center text-muted">Error cargando partidos: ' + err.message + '</p>';
    document.getElementById('featured').innerHTML = '<p class="text-center text-muted">Error: ' + err.message + '</p>';
  }
}

// Dibuja los paneles de ligas y sus partidos.
function renderLeagues(leagues){
  const container = document.getElementById('leaguesList');
  
  if (!container) {
    console.error('leaguesList container not found');
    return;
  }
  
  if (!leagues || !leagues.length) {
    container.innerHTML = '<p class="text-center text-muted">No hay partidos disponibles.</p>';
    return;
  }

  let html = '';
  
  leagues.forEach(league => {
    html += `<div class="league-panel mb-4">`;
    html += `<div class="league-title">${league.name || 'Sin nombre'}${league.country ? ' • ' + league.country : ''}</div>`;
    
    const matches = league.matches || [];
    if (matches.length === 0) {
      html += `<p class="text-muted">No hay partidos en esta liga.</p>`;
    } else {
      matches.forEach(m => {
        try {
          const kickoff = new Date(m.time).toLocaleString('es-ES', {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'});
          html += `<div class="match-card">`;
          html += `<div class="match-teams">`;
          html += `<div class="team-row"><span class="local-label">Local:</span> <strong>${m.home || 'Equipo'}</strong></div>`;
          html += `<div class="team-row"><span class="visit-label">Visitante:</span> <strong>${m.away || 'Equipo'}</strong></div>`;
          html += `</div>`;
          html += `<div class="match-details">`;
          html += `<div class="detail-row">📅 ${kickoff}</div>`;
          html += `<div class="detail-row">🏟️ ${m.stadium || 'Estadio'}</div>`;
          html += `<div class="odds-container">`;
          html += `<div class="odd-item"><span class="odd-label">Local</span><span class="odd-value">${m.home_odd || '-'}</span></div>`;
          html += `<div class="odd-item"><span class="odd-label">Empate</span><span class="odd-value">${m.draw_odd || '-'}</span></div>`;
          html += `<div class="odd-item"><span class="odd-label">Visitante</span><span class="odd-value">${m.away_odd || '-'}</span></div>`;
          html += `</div>`;
          html += `</div>`;
          html += `</div>`;
        } catch (e) {
          console.error('Error rendering match:', e, m);
        }
      });
    }
    
    html += `</div>`;
  });

  container.innerHTML = html;
}

// Dibuja los partidos destacados en la parte superior.
function renderFeatured(items){
  const container = document.getElementById('featured');
  if (!items || !items.length) {
    container.innerText = 'Sin partidos destacados.';
    return;
  }

  const cards = items.slice(0, 4).map((f, index) => `
    <div class="featured-card">
      <div class="featured-title">${f.competition || 'Próximo partido'}</div>
      <div class="featured-match">
        <div class="featured-team"><strong>${f.home}</strong></div>
        <div class="team-vs">VS</div>
        <div class="featured-team"><strong>${f.away}</strong></div>
      </div>
      <div class="featured-meta">🏟️ ${f.stadium || 'Estadio'}</div>
      <div class="featured-odds mb-2">
        <span class="odd-pill">${f.home_odd}</span>
        <span class="odd-label">Empate</span>
        <span class="odd-pill">${f.draw_odd}</span>
        <span class="odd-label">Visitante</span>
        <span class="odd-pill">${f.away_odd}</span>
      </div>
      <div id="countdown-${index}">-</div>
    </div>
  `).join('');

  container.innerHTML = `<div class="featured-grid">${cards}</div>`;

  items.slice(0, 4).forEach((f, index) => {
    try {
      const kickoff = new Date(f.kickoff);
      const el = document.getElementById(`countdown-${index}`);
      if (el) {
        updateCountdown(kickoff, el);
        if (window._countdownInterval) clearInterval(window._countdownInterval);
        window._countdownInterval = setInterval(() => updateCountdown(kickoff, el), 1000);
      }
    } catch (e) { console.warn('Invalid kickoff date', e); }
  });
}

// Actualiza la cuenta regresiva hasta el inicio de un partido.
function updateCountdown(kickoff, el){
  const now = new Date();
  const diff = kickoff - now;
  if(!el) return;
  if(diff<=0){ el.innerText = 'En juego / Finalizado'; return; }
  const hours = Math.floor(diff/1000/60/60);
  const minutes = Math.floor((diff/1000/60) % 60);
  const seconds = Math.floor((diff/1000) % 60);
  el.innerText = `${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
}

// initial fetch and polling every 10 seconds
fetchPartidos();
setInterval(fetchPartidos, 10000);
