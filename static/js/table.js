// Fehlernachricht-Container
var errorMessageDiv = document.getElementById('error-message');
let maxRows = 6;

document.getElementById('addRow').addEventListener('click', function(event) {
    var rowCount = document.getElementById('warenTabelle').getElementsByTagName('tbody')[0].getElementsByTagName('tr').length;
    
    event.preventDefault(); // Verhindert das Standard-Verhalten des Links

    if (rowCount < maxRows) {
        // Tabelle und tbody-Element finden
        var table = document.getElementById('warenTabelle').getElementsByTagName('tbody')[0];

        // Letzte Zeile finden, um deren <select> Optionen zu kopieren
        var lastRow = table.getElementsByTagName('tr')[rowCount - 1];
        var lastSelect = lastRow.querySelector('select'); // Das <select>-Element der letzten Zeile

        // Neue Zeile erstellen
        var newRow = document.createElement('tr');

        // Erstelle das neue <select>-Element und kopiere die Optionen
        var newSelect = document.createElement('select');
        newSelect.name = 'ware[]';
        newSelect.style.width = '100%';
        
        // Optionen vom letzten <select> in das neue <select> kopieren
        Array.from(lastSelect.options).forEach(function(option) {
            var newOption = document.createElement('option');
            newOption.value = option.value;
            newOption.text = option.text;
            newSelect.appendChild(newOption);
        });

        // HTML für die neue Zeile erstellen und das neue <select> Element einfügen
        newRow.innerHTML = 
            "<td><input type='number' name='anzahl[]' min='1' max='3' value='1' placeholder='Anzahl' style='width: 100%;'></td>" +
            "<td></td>" + // Leeres <td>, da wir das <select> manuell einfügen
            "<td><a href='#' class='removeRow'>Entfernen</a></td>";

        // Füge das neue <select> in die zweite Spalte ein
        newRow.cells[1].appendChild(newSelect);

        // Neue Zeile zur Tabelle hinzufügen
        table.appendChild(newRow);

        // Remove-Button-Event-Listener hinzufügen
        addRemoveFunctionality(newRow);

        // Zeilenanzahl erhöhen
        rowCount++;

        // Fehlernachricht ausblenden, falls sie sichtbar ist
        errorMessageDiv.style.display = 'none';
    } else {
        var errorCode = this.getAttribute('data-error');
        errorMessageDiv.textContent = 'Fehlercode: ' + errorCode + ' - Es können maximal ' + maxRows + ' Zeilen hinzugefügt werden.';
        errorMessageDiv.style.display = 'block'; // Fehlernachricht sichtbar machen
    }    
});

// Funktion, um eine Zeile zu entfernen
function addRemoveFunctionality(row) {
    row.querySelector('.removeRow').addEventListener('click', function(event) {
        event.preventDefault(); // Verhindert das Standard-Verhalten des Links
        
		var rowCount = document.getElementById('warenTabelle').getElementsByTagName('tbody')[0].getElementsByTagName('tr').length;

        if (rowCount > 1) { // Überprüfen, ob mehr als eine Zeile vorhanden ist
            row.remove(); // Entfernt die Zeile
            errorMessageDiv.style.display = 'none'; // Versteckt die Fehlermeldung, falls sie zuvor angezeigt wurde
        } else {
            // Zeige die Fehlermeldung an, dass die letzte Zeile nicht entfernt werden kann
            errorMessageDiv.textContent = "Letzte Zeile kann nicht entfernt werden!";
            errorMessageDiv.style.display = 'block'; // Fehlernachricht sichtbar machen
        }
    });
}

// Initiale Remove-Funktion für bestehende Zeilen hinzufügen
document.querySelectorAll('.removeRow').forEach(function(element) {
    addRemoveFunctionality(element.closest('tr'));
});
