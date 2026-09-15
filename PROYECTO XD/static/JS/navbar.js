// Navbar interaction script: search autocomplete and scroll state
(function(){
  'use strict';

  function onScroll(){
    var nav = document.querySelector('.navbar');
    if(!nav) return;
    if(window.scrollY > 30){
      nav.classList.add('nav-scrolled');
    } else {
      nav.classList.remove('nav-scrolled');
    }
  }

  function initAutocomplete(){
    var searchInput = document.getElementById('searchInput');
    var autocompleteList = document.getElementById('autocompleteList');

    if (!searchInput || !autocompleteList) return;

    function hideResults(){
      autocompleteList.classList.remove('active');
      autocompleteList.innerHTML = '';
    }

    function showResults(results){
      autocompleteList.classList.add('active');
      autocompleteList.innerHTML = results.map(function(result){
        var label = result.nombre || '';
        var type = result.type || '';
        var id = result.id || '';
        return '<div class="autocomplete-item" data-type="'+type+'" data-id="'+id+'">'
          + '<strong>'+label+'</strong> <span class="autocomplete-badge">'+type.toUpperCase()+'</span>'
          + '</div>';
      }).join('');

      Array.prototype.forEach.call(autocompleteList.querySelectorAll('.autocomplete-item'), function(item){
        item.addEventListener('click', function(){
          var type = item.dataset.type;
          var label = item.querySelector('strong') ? item.querySelector('strong').textContent.trim() : '';
          if (!label) return;
          // Redirect to the search page with query param so server shows the matching info
          var url = '/search?q=' + encodeURIComponent(label);
          document.location.href = url;
        });
      });
    }

    searchInput.addEventListener('input', function(e){
      var query = e.target.value.trim();
      if (query.length < 1){
        hideResults();
        return;
      }

      fetch('/autocomplete?q=' + encodeURIComponent(query))
        .then(function(response){ return response.json(); })
        .then(function(results){
          if (Array.isArray(results) && results.length > 0){
            showResults(results);
          } else {
            hideResults();
          }
        })
        .catch(function(error){
          console.error(error);
          hideResults();
        });
    });

    document.addEventListener('click', function(event){
      if (!event.target.closest('.navbar-search-container')){
        hideResults();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    onScroll();
    initAutocomplete();
    window.addEventListener('scroll', onScroll, {passive:true});
  });
})();
