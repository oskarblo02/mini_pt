fetch('minipt.json')
  .then(response => response.json())
  .then(data => {
    let container = document.getElementById('tableContainer');
    for (let setName in data) {
      let set = data[setName];
      let table = document.createElement('table');
      let tableHead = document.createElement('thead');
      let tableBody = document.createElement('tbody');

      let headRow = document.createElement('tr');
      let headCell1 = document.createElement('th');
      headCell1.textContent = 'Rep Count';
      let headCell2 = document.createElement('th');
      headCell2.textContent = 'Rep Time';
      let headCell3 = document.createElement('th');
      headCell3.textContent = 'EEPF';
      headRow.appendChild(headCell1);
      headRow.appendChild(headCell2);
      headRow.appendChild(headCell3);
      tableHead.appendChild(headRow);

      for (let key in set) {
        let rep = set[key];
        let row = document.createElement('tr');
        let countCell = document.createElement('td');
        countCell.textContent = rep.rep_count;
        let timeCell = document.createElement('td');
        timeCell.textContent = rep.rep_time.toFixed(2) + " s";
        let eepfCell = document.createElement('td');
        eepfCell.textContent = rep.EEPF.toFixed(2) + " %";
        row.appendChild(countCell);
        row.appendChild(timeCell);
        row.appendChild(eepfCell);
        tableBody.appendChild(row);
      }

      table.appendChild(tableHead);
      table.appendChild(tableBody);
      container.appendChild(table);

      let setTitle = document.createElement('div');
      setTitle.classList.add('set-title');
      setTitle.textContent = setName;
      container.insertBefore(setTitle, table);
    }
  })
  .catch(error => console.error(error));
