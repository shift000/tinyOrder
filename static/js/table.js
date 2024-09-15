// Globale Variable für die Zeilenanzahl
        //var rowCount = document.getElementById('warenTabelle').getElementsByTagName('tbody')[0].getElementsByTagName('tr').length;

        // Fehlernachricht-Container
        var errorMessageDiv = document.getElementById('error-message');
        let maxRows = 6;

        document.getElementById('addRow').addEventListener('click', function(event) {
            var rowCount = document.getElementById('warenTabelle').getElementsByTagName('tbody')[0].getElementsByTagName('tr').length;
            
            event.preventDefault(); // Verhindert das Standard-Verhalten des Links

            if (rowCount < maxRows) {
                // Tabelle und tbody-Element finden
                var table = document.getElementById('warenTabelle').getElementsByTagName('tbody')[0];
    
                // Neue Zeile erstellen
                var newRow = document.createElement('tr');
    
                // HTML für die neue Zeile
                newRow.innerHTML = 
                    "<td><input type='number' name='anzahl[]' min='1' max='3' value='1' placeholder='Anzahl' style='width: 100%;'></td>" +
                    "<td>" +
                    "<select name='ware[]' style='width: 100%;'>" +
                    "<option value='apfel'>Apfel</option>" +
                    "<option value='banane'>Banane</option>" +
                    "<option value='orange'>Orange</option>" +
                    "</select>" +
                    "</td>" +
                    "<td><a href='#' class='removeRow'>Entfernen</a></td>";

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
                row.remove(); // Entfernt die Zeile
            });
        }

        // Initiale Remove-Funktion für bestehende Zeilen hinzufügen
        document.querySelectorAll('.removeRow').forEach(function(element) {
            addRemoveFunctionality(element.closest('tr'));
        });