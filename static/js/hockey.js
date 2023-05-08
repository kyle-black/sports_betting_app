document.addEventListener("DOMContentLoaded", function () {
    const expandButtons = document.querySelectorAll(".expand-btn");
  
    expandButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const bookmakerOdds = btn.parentElement.querySelectorAll(".bookmaker-odds");
  
        bookmakerOdds.forEach(function (oddsElem) {
          if (oddsElem.style.display === "none") {
            oddsElem.style.display = "table-cell";
            btn.textContent = "Collapse Odds";
          } else {
            oddsElem.style.display = "none";
            btn.textContent = "Expand Odds";
          }
        });
      });
    });
  });
  