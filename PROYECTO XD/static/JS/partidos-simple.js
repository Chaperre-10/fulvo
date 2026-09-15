// Estado global de la vista de partidos y de la predicción seleccionada.
const state = {
  leagues: [],
  selectedLeague: 'Todos',
  selectedMatch: null,
  prediction: null,
  userPredictions: [],
  currentTab: 'live'
};

// Devuelve partidos de respaldo cuando la API no entrega información.
function getFallbackLeagueData() {
  return [
    {
      name: 'CONMEBOL Libertadores',
      matches: [
        { home: 'Mirassol SP', away: 'LDU Quito', time: '2026-08-13T17:00:00', stadium: 'Estádio José Jorge Damous', home_odd: '2.10', draw_odd: '3.25', away_odd: '3.45' },
        { home: 'Rosario Central', away: 'Corinthians', time: '2026-08-13T19:30:00', stadium: 'Estadio Gigante de Arroyito', home_odd: '1.92', draw_odd: '3.35', away_odd: '4.05' },
        { home: 'CS U Craiova', away: 'Kuopion Palloseura', time: '2026-08-13T12:00:00', stadium: 'Ion Oblemenco Stadium', home_odd: '2.30', draw_odd: '3.40', away_odd: '2.75' },
        { home: 'AC Omonia Nicosia', away: 'Lincoln Red Imps FC', time: '2026-08-13T12:00:00', stadium: 'New GSP Stadium', home_odd: '1.95', draw_odd: '3.55', away_odd: '3.60' }
      ]
    },
    {
      name: 'UEFA Europa League',
      matches: [
        { home: 'KI Klaksvik', away: 'Lech Poznan', time: '2026-08-13T12:30:00', stadium: 'Svangaskali', home_odd: '2.40', draw_odd: '3.25', away_odd: '2.75' },
        { home: 'Real Madrid', away: 'Barcelona', time: '2026-08-16T18:30:00', stadium: 'Santiago Bernabéu', home_odd: '2.05', draw_odd: '3.50', away_odd: '3.15' },
        { home: 'Atlético de Madrid', away: 'Valencia', time: '2026-08-17T21:00:00', stadium: 'Wanda Metropolitano', home_odd: '1.80', draw_odd: '3.45', away_odd: '4.25' }
      ]
    },
    {
      name: 'La Liga',
      matches: [
        { home: 'Real Madrid', away: 'Barcelona', time: '2026-08-16T18:30:00', stadium: 'Santiago Bernabéu', home_odd: '2.05', draw_odd: '3.50', away_odd: '3.15' },
        { home: 'Atlético de Madrid', away: 'Valencia', time: '2026-08-17T21:00:00', stadium: 'Wanda Metropolitano', home_odd: '1.80', draw_odd: '3.45', away_odd: '4.25' }
      ]
    },
    {
      name: 'Premier League',
      matches: [
        { home: 'Manchester City', away: 'Arsenal', time: '2026-08-16T15:30:00', stadium: 'Etihad Stadium', home_odd: '2.30', draw_odd: '3.40', away_odd: '2.75' },
        { home: 'Liverpool', away: 'Chelsea', time: '2026-08-17T17:00:00', stadium: 'Anfield', home_odd: '1.85', draw_odd: '3.60', away_odd: '4.20' }
      ]
    },
    {
      name: 'Serie A',
      matches: [
        { home: 'Juventus', away: 'Inter', time: '2026-08-15T18:00:00', stadium: 'Allianz Stadium', home_odd: '2.65', draw_odd: '3.20', away_odd: '2.55' },
        { home: 'Mirassol SP', away: 'LDU Quito', time: '2026-08-13T17:00:00', stadium: 'Estádio José Jorge Damous', home_odd: '2.10', draw_odd: '3.25', away_odd: '3.45' }
      ]
    },
    {
      name: 'MLS',
      matches: [
        { home: 'Inter Miami', away: 'LA Galaxy', time: '2026-08-18T22:00:00', stadium: 'Chase Stadium', home_odd: '1.90', draw_odd: '3.50', away_odd: '3.25' }
      ]
    }
  ];
}

// Orden preferido para mostrar las ligas en la interfaz.
const leaguePriorityOrder = [
  'Premier League',
  'La Liga',
  'Serie A',
  'Liga BetPlay Dimayor',
  'UEFA Champions League',
  'UEFA Europa League',
  'CONMEBOL Libertadores',
  'MLS'
];

// Obtiene la prioridad numérica de una liga según su nombre.
function getLeaguePriority(name) {
  const index = leaguePriorityOrder.indexOf(name || '');
  return index === -1 ? 999 : index;
}

// Ordena las ligas antes de renderizarlas en pantalla.
function sortLeaguesForDisplay(leagues) {
  return (leagues || []).slice().sort(function(a, b) {
    const aPriority = getLeaguePriority(a && a.name);
    const bPriority = getLeaguePriority(b && b.name);
    if (aPriority !== bPriority) return aPriority - bPriority;
    return String(a && a.name || '').localeCompare(String(b && b.name || ''));
  });
}

// Construye la dirección de la imagen representativa de un equipo.
function getTeamBadge(teamName) {
  const normalized = (teamName || 'T').trim();
  const initials = normalized.split(/\s+/).slice(0, 2).map(function(part) {
    return part.charAt(0).toUpperCase();
  }).join('').slice(0, 2) || 'T';
  return initials;
}

// Genera el HTML de una tarjeta individual de partido.
function buildMatchCard(match, isSelected) {
  const selectedClass = isSelected ? ' selected' : '';
  const matchKey = (match && (match.key || (match.home || 'home') + '-' + (match.away || 'away') + '-' + (match.time || ''))) || '';
  const homeOdds = match && match.home_odd ? String(match.home_odd).trim() : '2.20';
  const drawOdds = match && match.draw_odd ? String(match.draw_odd).trim() : '3.20';
  const awayOdds = match && match.away_odd ? String(match.away_odd).trim() : '3.10';
  const homeName = match && match.home ? String(match.home).trim() : 'Local';
  const awayName = match && match.away ? String(match.away).trim() : 'Visitante';
  const timeStr = match && match.time ? String(match.time).trim() : '';
  const stadiumStr = match && match.stadium ? String(match.stadium).trim() : '';

  return [
    '<div class="match-card' + selectedClass + '" data-match-key="' + (matchKey || '') + '">',
    '<div class="match-header">',
    '<div class="team-block">',
    '<div class="team-line">',
    '<span class="team-badge">' + getTeamBadge(homeName) + '</span>',
    '<div class="team-name"><strong>' + homeName + '</strong></div>',
    '</div>',
    '<div class="team-line">',
    '<span class="team-badge">' + getTeamBadge(awayName) + '</span>',
    '<div class="team-name"><strong>' + awayName + '</strong></div>',
    '</div>',
    '</div>',
    '<div class="match-side">',
    '<div class="match-meta">' + timeStr + '</div>',
    '<div class="match-meta">' + stadiumStr + '</div>',
    '</div>',
    '</div>',
    '<div class="match-odds">',
    '<div class="odd-pill"><span class="odd-label">1</span><span class="odd-value">' + homeOdds + '</span></div>',
    '<div class="odd-pill"><span class="odd-label">X</span><span class="odd-value">' + drawOdds + '</span></div>',
    '<div class="odd-pill"><span class="odd-label">2</span><span class="odd-value">' + awayOdds + '</span></div>',
    '</div>',
    '</div>'
  ].join('');
}

// Genera la lista de partidos disponibles para predecir.
function buildPredictionList(matches) {
  if (!matches || !matches.length) {
    return '<p class="text-center text-muted">No hay partidos disponibles para esta liga.</p>';
  }

  return '<div class="prediction-match-grid">' + matches.map(function(match, index) {
    const active = state.selectedMatch && state.selectedMatch.key === match.key ? 'active' : '';
    const homeName = match.home ? String(match.home).trim() : 'Local';
    const awayName = match.away ? String(match.away).trim() : 'Visitante';
    const timeStr = match.time ? String(match.time).trim() : '';
    return '<button type="button" class="prediction-match-card ' + active + '" data-key="' + (match.key || index) + '">' +
      '<strong>' + homeName + ' vs ' + awayName + '</strong>' +
      '<span>' + timeStr + '</span>' +
      '</button>';
  }).join('') + '</div>';
}

// Dibuja las opciones del formulario de predicción.
function renderPredictionForm() {
  const container = document.getElementById('predictionForm');
  if (!container) return;

  const match = state.selectedMatch;
  if (!match) {
    container.innerHTML = '<p class="text-center text-muted">Selecciona un partido para predecir.</p>';
    return;
  }

  const savedPrediction = state.userPredictions.find(function(item) {
    return item.match_key === match.key;
  });
  if (savedPrediction) {
    state.prediction = savedPrediction.prediction;
  }

  const customPredictionValue = (state.prediction && !['Local', 'Empate', 'Visitante'].includes(state.prediction)) ? state.prediction : '';
  const resultText = state.prediction ? 'Tu predicción: ' + state.prediction : 'No has elegido aún';
  const homeName = match.home ? String(match.home).trim() : 'Local';
  const awayName = match.away ? String(match.away).trim() : 'Visitante';

  container.innerHTML = [
    '<div class="prediction-form">',
    '<h3>' + homeName + ' vs ' + awayName + '</h3>',
    '<div class="prediction-options">',
    '<label class="prediction-option"><input type="radio" name="predictionResult" value="Local" ' + (state.prediction === 'Local' ? 'checked' : '') + '> Local</label>',
    '<label class="prediction-option"><input type="radio" name="predictionResult" value="Empate" ' + (state.prediction === 'Empate' ? 'checked' : '') + '> Empate</label>',
    '<label class="prediction-option"><input type="radio" name="predictionResult" value="Visitante" ' + (state.prediction === 'Visitante' ? 'checked' : '') + '> Visitante</label>',
    '</div>',
    '<div class="prediction-custom">',
    '<label for="customPrediction">Resultado exacto (ej. 2-1, 1-0, 3-3)</label>',
    '<input id="customPrediction" type="text" name="customPrediction" value="' + customPredictionValue + '" placeholder="Escribe el marcador que crees" />',
    '</div>',
    '<div class="prediction-result-box">' + resultText + '</div>',
    '<button type="button" class="prediction-submit">Guardar predicción</button>',
    '</div>'
  ].join('');

  const radioInputs = container.querySelectorAll('input[name="predictionResult"]');
  radioInputs.forEach(function(input) {
    input.addEventListener('change', function() {
      state.prediction = this.value;
      renderPredictionForm();
    });
  });

  const customInput = container.querySelector('#customPrediction');
  if (customInput) {
    customInput.addEventListener('input', function() {
      state.prediction = this.value.trim();
      const box = container.querySelector('.prediction-result-box');
      if (box) {
        box.textContent = this.value.trim() ? 'Tu predicción: ' + this.value.trim() : 'No has elegido aún';
      }
    });
  }

  const saveButton = container.querySelector('.prediction-submit');
  if (saveButton) {
    saveButton.addEventListener('click', function() {
      if (!state.selectedMatch) return;

      const finalPrediction = (state.prediction || '').trim() || 'Local';

      fetch('/api/predictions', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          match_key: state.selectedMatch.key,
          league_name: state.selectedLeague === 'Todos' ? (state.selectedMatch.league_name || 'Liga BetPlay Dimayor') : state.selectedLeague,
          home_team: state.selectedMatch.home,
          away_team: state.selectedMatch.away,
          kickoff: state.selectedMatch.time,
          prediction: finalPrediction
        })
      })
      .then(function(response) { return response.json(); })
      .then(function(data) {
        if (data && data.success) {
          fetchUserPredictions();
          const box = container.querySelector('.prediction-result-box');
          if (box) {
            box.textContent = 'Tu predicción: ' + finalPrediction + ' para ' + (state.selectedMatch.home || 'Local') + ' vs ' + (state.selectedMatch.away || 'Visitante');
          }
        }
      })
      .catch(function(error) {
        console.error('Error saving prediction:', error);
      });
    });
  }
}

// Actualiza el panel lateral con la predicción activa.
function renderPredictionPanel() {
  const panel = document.getElementById('predictionPanel');
  const container = document.getElementById('predictionMatchList');
  const formContainer = document.getElementById('predictionForm');

  if (!panel || !formContainer) return;

  if (!state.selectedMatch) {
    panel.classList.remove('visible');
    if (container) container.innerHTML = '';
    formContainer.innerHTML = '';
    return;
  }

  panel.classList.add('visible');

  const selectedLeague = state.selectedLeague === 'Todos'
    ? (state.selectedMatch.league_name || 'Liga')
    : state.selectedLeague;

  const leagueMatches = (state.leagues || []).find(function(item) {
    return item.name === selectedLeague;
  });

  const matches = (leagueMatches && leagueMatches.matches ? leagueMatches.matches : []).map(function(match, index) {
    return Object.assign({}, match, {
      key: (match.home || 'home') + '-' + (match.away || 'away') + '-' + (match.time || index),
      league_name: selectedLeague
    });
  });

  if (container) {
    container.innerHTML = buildPredictionList(matches);
    container.querySelectorAll('.prediction-match-card').forEach(function(card) {
      card.addEventListener('click', function() {
        const key = this.dataset.key;
        const match = matches.find(function(item) { return String(item.key) === String(key); });
        if (match) {
          state.selectedMatch = match;
          state.prediction = null;
          renderPredictionPanel();
        }
      });
    });
  }

  renderPredictionForm();
}

// Determina la etiqueta visual correspondiente al estado del partido.
function getMatchCategoryLabel(match) {
  if (!match || !match.time) {
    return 'Apertura de temporada';
  }

  const kickoff = new Date(match.time);
  const now = new Date();
  const startOfToday = new Date(now);
  startOfToday.setHours(0, 0, 0, 0);
  const startOfTomorrow = new Date(startOfToday);
  startOfTomorrow.setDate(startOfTomorrow.getDate() + 1);
  const startOfDayAfterTomorrow = new Date(startOfToday);
  startOfDayAfterTomorrow.setDate(startOfDayAfterTomorrow.getDate() + 2);

  if (kickoff >= startOfToday && kickoff < startOfTomorrow && kickoff >= now) {
    return 'Hoy';
  }
  if (kickoff >= startOfTomorrow && kickoff < startOfDayAfterTomorrow) {
    return 'Mañana';
  }
  if (kickoff >= startOfToday && kickoff < now) {
    return 'Ya jugados hoy';
  }
  return 'Apertura de temporada';
}

// Renderiza todas las ligas y sus partidos en la vista principal.
function renderLeagues() {
  const leaguesContainer = document.getElementById('leaguesList');
  if (!leaguesContainer) return;

  const visibleLeagues = sortLeaguesForDisplay(
    state.selectedLeague === 'Todos'
      ? state.leagues
      : state.leagues.filter(function(item) {
          return item.name === state.selectedLeague;
        })
  );

  if (!visibleLeagues || !visibleLeagues.length) {
    leaguesContainer.innerHTML = '<p class="text-center text-muted">No hay partidos disponibles.</p>';
    return;
  }

  const categories = {
    'Hoy': [],
    'Mañana': [],
    'Ya jugados hoy': [],
    'Apertura de temporada': []
  };

  visibleLeagues.forEach(function(league) {
    const matches = (league.matches || []).slice().sort(function(a, b) {
      return String(a.time || '').localeCompare(String(b.time || ''));
    });

    matches.forEach(function(match) {
      const category = getMatchCategoryLabel(match);
      categories[category].push(Object.assign({}, match, {
        key: (match.home || 'home') + '-' + (match.away || 'away') + '-' + (match.time || ''),
        league_name: league.name
      }));
    });
  });

  let html = '';
  const order = ['Hoy', 'Mañana', 'Ya jugados hoy', 'Apertura de temporada'];
  order.forEach(function(categoryLabel) {
    const categoryMatches = categories[categoryLabel] || [];
    if (!categoryMatches.length) return;

    html += '<div class="calendar-section">';
    html += '<div class="calendar-section-title">' + categoryLabel + '</div>';
    html += '<div class="calendar-section-grid">';

    categoryMatches.forEach(function(match) {
      const isSelected = state.selectedMatch && state.selectedMatch.key === match.key;
      html += buildMatchCard(match, isSelected);
    });

    html += '</div>';
    html += '</div>';
  });

  leaguesContainer.innerHTML = html;

  document.querySelectorAll('.match-card').forEach(function(card) {
    card.addEventListener('click', function() {
      const key = this.dataset.matchKey;
      let matchToSelect = null;

      order.forEach(function(categoryLabel) {
        if (matchToSelect) return;
        const categoryMatches = categories[categoryLabel] || [];
        matchToSelect = categoryMatches.find(function(match) {
          return String(match.key) === String(key);
        });
      });

      if (matchToSelect) {
        state.selectedMatch = matchToSelect;
        state.prediction = null;
        renderLeagues();
        renderPredictionPanel();
      }
    });
  });
}

// Renderiza el resumen de predicciones del usuario.
function renderPredictionDashboard() {
  const leaguesContainer = document.getElementById('leaguesList');
  if (!leaguesContainer) return;

  const predictions = (state.userPredictions || []).slice().sort(function(a, b) {
    const aDate = a && a.kickoff ? new Date(a.kickoff).getTime() : 0;
    const bDate = b && b.kickoff ? new Date(b.kickoff).getTime() : 0;
    return bDate - aDate;
  });

  if (!predictions.length) {
    leaguesContainer.innerHTML = [
      '<div class="empty-state">',
      '<h3>Sin predicciones todavía</h3>',
      '<p>Selecciona un partido desde Live y guarda tu pronóstico para que te aparezca aquí.</p>',
      '</div>'
    ].join('');
    return;
  }

  const html = predictions.map(function(prediction) {
    const matchDate = prediction.kickoff ? new Date(prediction.kickoff).toLocaleString('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    }) : 'Sin fecha';

    return [
      '<div class="prediction-item" data-prediction-key="' + (prediction.match_key || '') + '">',
      '<div class="prediction-item-header">',
      '<strong>' + (prediction.home_team || 'Local') + ' vs ' + (prediction.away_team || 'Visitante') + '</strong>',
      '<span class="prediction-tag">' + String(prediction.prediction || 'Sin pronóstico') + '</span>',
      '</div>',
      '<div class="prediction-item-meta">',
      '<span>' + (prediction.league_name || 'Liga') + '</span>',
      '<span>' + matchDate + '</span>',
      '</div>',
      '<button type="button" class="prediction-open-btn" data-match-key="' + (prediction.match_key || '') + '">Abrir partido</button>',
      '</div>'
    ].join('');
  }).join('');

  leaguesContainer.innerHTML = '<div class="prediction-dashboard">' + html + '</div>';

  document.querySelectorAll('.prediction-open-btn').forEach(function(button) {
    button.addEventListener('click', function() {
      const matchKey = this.dataset.matchKey;
      const match = (state.leagues || []).flatMap(function(league) {
        return (league.matches || []).map(function(item) {
          return Object.assign({}, item, {
            key: (item.home || 'home') + '-' + (item.away || 'away') + '-' + (item.time || ''),
            league_name: league.name
          });
        });
      }).find(function(item) { return String(item.key) === String(matchKey); });

      if (match) {
        state.selectedMatch = match;
        state.currentTab = 'live';
        renderTabButtons();
        renderLeagues();
        renderPredictionPanel();
      }
    });
  });
}

// Crea los botones para cambiar entre categorías deportivas.
function renderTabButtons() {
  const activeTab = state.currentTab || 'live';
  document.querySelectorAll('.sports-tab').forEach(function(tab) {
    const isActive = tab.dataset.tab === activeTab;
    tab.classList.toggle('active', isActive);
  });
}

// Coordina el renderizado completo de la vista de partidos.
function renderSportsView() {
  renderTabButtons();
  if (state.currentTab === 'predictions') {
    renderPredictionDashboard();
    return;
  }
  renderLeagues();
  renderPredictionPanel();
}

async function fetchUserPredictions() {
  try {
    const response = await fetch('/api/predictions', { method: 'GET', credentials: 'include' });
    if (!response.ok) return;
    const data = await response.json();
    state.userPredictions = data.predictions || [];
    if (state.selectedMatch) {
      const saved = state.userPredictions.find(function(item) {
        return item.match_key === state.selectedMatch.key;
      });
      state.prediction = saved ? saved.prediction : null;
    }
    if (state.currentTab === 'predictions') {
      renderPredictionDashboard();
    } else {
      renderPredictionForm();
    }
  } catch (error) {
    console.error('Error fetching predictions:', error);
  }
}

async function fetchPartidos() {
  console.log('fetchPartidos called');
  try {
    const response = await fetch('/api/partidos', {
      method: 'GET',
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('HTTP error! status: ' + response.status);
    }

    const data = await response.json();
    state.leagues = data.leagues && data.leagues.length ? data.leagues : getFallbackLeagueData();

    const leagueFilter = document.getElementById('leagueFilter');
    if (leagueFilter) {
      const options = Array.from(new Set(state.leagues.map(function(item) { return item.name; }))).filter(Boolean);
      const existing = Array.from(leagueFilter.options).map(function(option) { return option.value; });
      options.forEach(function(name) {
        if (!existing.includes(name)) {
          const option = document.createElement('option');
          option.value = name;
          option.textContent = name;
          leagueFilter.appendChild(option);
        }
      });
      if (!state.selectedLeague || !options.includes(state.selectedLeague)) {
        state.selectedLeague = 'Todos';
      }
      leagueFilter.value = state.selectedLeague;
      leagueFilter.onchange = function() {
        state.selectedLeague = this.value;
        renderSportsView();
      };
    }

    renderSportsView();
    fetchUserPredictions();
  } catch (error) {
    console.error('Error in fetchPartidos:', error);
    const leaguesContainer = document.getElementById('leaguesList');
    if (leaguesContainer) {
      leaguesContainer.innerHTML = '<p>Error: ' + error.message + '</p>';
    }
  }
}

// Inicializa la vista cuando el documento ya está disponible en el navegador.
window.addEventListener('DOMContentLoaded', function() {
  const filterSelect = document.getElementById('leagueFilter');
  if (filterSelect) {
    filterSelect.value = state.selectedLeague;
    filterSelect.addEventListener('change', function() {
      state.selectedLeague = this.value;
      state.selectedMatch = null;
      renderSportsView();
    });
  }

  document.querySelectorAll('.sports-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      state.currentTab = this.dataset.tab || 'live';
      renderSportsView();
    });
  });

  fetchPartidos();
});
