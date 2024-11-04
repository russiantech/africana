    /** READ / DISPLAY */
    // ==============================================================
    document.addEventListener('DOMContentLoaded', function () {
        // Load main products on page load
        // fetchMainProducts();
    
        // Add event listeners for each tab to load data when clicked
        document.querySelector('#pills-extraction-tab').addEventListener('click', fetchExtractedItem);
    });
    
    function fetchExtractedItem() {
        fetch('api/extractions')
            .then(response => response.json())
            .then(data => {
                //console.log(data.data.items)
                populateTable2(data.data.items, 'extractionTableBody');
            })
            .catch(error => console.error('Error fetching main products:', error));
    }
    
    function populateTable2(items, tableId) {
        const tableBody = document.querySelector(`#${tableId}`);
        
        // Check if items is defined and has the expected structure
        if (items.length > 0) {
            //console.log(items)
            tableBody.innerHTML = ''; // Clear existing rows
            
            items.forEach(item => {
                let row = `
                    <tr data-item-id="${item.id}">
                        <td>${item.id}</td>
                        <td>${item.extracted_title}</td>
                        <td>${item.product_title || 'N/A'}</td>
                        <td>${item.extracted_qty || 0}</td>
                        <td>${item.created_at || 'Not available'}</td>
                        <td>
                            <div class="d-flex align-items-center list-action"> 
                                <button class="badge bg-success mr-2 border-none" onclick="makeRowEditable2(${item.id}, ${item.apportion_id || null })"><i class="ri-pencil-line mr-0"></i></button>
                                <button class="badge bg-warning mr-2 border-none" onclick="confirmDeleteExtraction(${item.id})"><i class="ri-delete-bin-line mr-0"></i></button>
                            </div>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
            

        } else {
            tableBody.innerHTML = '<tr><td colspan="6">No items found.</td></tr>';
        }

    }

    /* INSERTING */
// ============================================================== //
document.addEventListener('DOMContentLoaded', function () {
    // Attach click listener to the "Add New Product" button
    document.querySelector('.new-product-row-btn2').addEventListener('click', create_editable_row2);
});

function create_editable_row2() {
    let tableBody = document.querySelector("#extractionTableBody");

    // Prevent adding multiple editable rows
    if (document.querySelector("#extractionTableBody .editable-row2")) {
        response_modal('You already have a row being edited.');
        return;
    }

    // Create a new row with input fields
    let newRow = document.createElement("tr");
    newRow.classList.add("editable-row2");
    newRow.innerHTML = `
        <td>-</td>
        <td><input type="text" class="form-control" id="extracted_title" placeholder="Like 3 Bag From Rice"></td>
        <td>
            <select class="form-control" id="apportion_id">
                <option value="">Loading apportioned items...</option>
            </select>
        </td>
        <td><input type="number" class="form-control" id="extracted_qty" value="0" placeholder="Extracted Qty"></td>
        <td>-</td>
        <td>
            <button class="btn btn-success" onclick="submitNewExtraction()"><i class="las la-plus mr-0"></i></button>
            <button class="btn btn-secondary" onclick="cancelNewItem()"><i class="ri-close-line"></i></button>
        </td>
    `;

    // Insert the new row at the top of the table body
    tableBody.insertBefore(newRow, tableBody.firstChild);

    // Load apportioned items dynamically
    loadApportionedItems();

}

function submitNewExtraction() {
    // Get values from inputs
    let extractedTitle = document.getElementById("extracted_title").value;
    let extractedQty = document.getElementById("extracted_qty").value;
    let apportionId = document.getElementById("apportion_id").value;

    if (!extractedTitle || !extractedQty || !apportionId) {
        response_modal('Please fill in all fields as required.');
        return;
    }

    let data = {
        extracted_title: extractedTitle,
        extracted_qty: extractedQty,
        apportion_id: apportionId
    };

    fetch('/api/extractions', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // Prepare the new row with saved data
            let tableBody = document.querySelector("#extractionTableBody");
            let newRow = document.createElement("tr");
            newRow.dataset.itemId = result.data.id;
            newRow.innerHTML = `
                <td>${result.data.id}</td>
                <td>${result.data.extracted_title}</td>
                <td>${result.data.product_title || 'N/A'}</td>
                <td>${result.data.extracted_qty || 0}</td>
                <td>${result.data.created_at || 'Not available'}</td>
                <td>
                    <div class="d-flex align-items-center list-action"> 
                        <button class="badge bg-success mr-2 border-none" onclick="makeRowEditable2(${result.data.id}, ${result.data.apportion_id || null })"><i class="ri-pencil-line mr-0"></i></button>
                        <button class="badge bg-warning mr-2 border-none" onclick="confirmDeleteExtraction(${result.data.id})"><i class="ri-delete-bin-line mr-0"></i></button>
                    </div>
                </td>
            `;
            tableBody.insertBefore(newRow, tableBody.firstChild);
            document.querySelector("#extractionTableBody .editable-row2").remove();
            response_modal(result.message);
        } else {
            response_modal(`Error adding product - ${result.error}`);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        response_modal("A network error occurred: " + error.message);
    });
}

function loadApportionedItems(selectedApportionId=null) {
    fetch('/api/apportions')
        .then(response => response.json())
        .then(result => {
            console.log(result);
            if (result.success) {
                const selectElement = document.getElementById("apportion_id");
                selectElement.innerHTML = '<option value="">Select Apportion</option>'; // Default option

                // Populate options with apportioned items
                result.data.items.forEach(item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.product_title;

                    // Set the initial selected item
                    if (item.id === selectedApportionId) {
                        option.selected = true;
                    }

                    selectElement.appendChild(option);
                });
            } else {
                console.error("Error fetching apportioned items:", result.error);
            }
        })
        .catch(error => console.error("Network error:", error));
}

function cancelNewItem() {
    document.querySelector("#extractionTableBody .editable-row2").remove();
}

/* UPDATING */
// ======================================================================== //


function makeRowEditable2(productId, currentApportionId) {
    if (document.querySelector(".editable-row")) {
        response_modal("You already have a row being edited.");
        return;
    }

    let row = document.querySelector(`tr[data-item-id="${productId}"]`);
    row.classList.add("editable-row");

    let extractedTitle = row.children[1].textContent.trim();
    let extractedQty = row.children[3].textContent.trim();

    row.innerHTML = `
        <td>-</td>
        <td><input type="text" value="${extractedTitle}" class="form-control" id="edit_extracted_title" placeholder="Like 3 Bag From Rice"></td>
        <td>
            <select class="form-control" id="apportion_id">
                <option value="">Loading apportioned items...</option>
            </select>
        </td>
        <td><input type="number" value="${extractedQty}" class="form-control" id="edit_extracted_qty" value="0" placeholder="Extracted Qty"></td>
        <td>-</td>
        <td>
            <button class="btn btn-success" onclick="submitUpdatedExtraction(${productId})"><i class="las la-save mr-0"></i></button>
            <button class="btn btn-secondary" onclick="cancelEdit()"><i class="ri-close-line"></i></button>
        </td>
    `;

    // Load apportioned items and mark the current apportion as selected
    loadApportionedItems(currentApportionId);
}



function submitUpdatedExtraction(productId) {

    /*  */
     // Get values from inputs
     let extractedTitle = document.getElementById("edit_extracted_title").value;
     let extractedQty = document.getElementById("edit_extracted_qty").value;
    //  let extractedId = parseInt(document.getElementById("edit_extracted_id").value);
     let apportionId = parseInt(document.getElementById("apportion_id").value);

     if (!extractedTitle || !extractedQty || !apportionId) {
         response_modal('Please fill in all fields as required.');
         return;
     }
 
     let data = {
         extracted_title: extractedTitle,
         extracted_qty: extractedQty,
        //  extracted_id: extractedId,
         apportion_id: apportionId
     };

    fetch(`/api/extractions/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            response_modal(result.message);
            // Optionally reload table or update the row dynamically here
        } else {
            response_modal(`Error: ${result.error}`);
        }
    })
    .catch(error => response_modal(`Error: ${error}`));
}

function cancelEdit() {
    document.querySelector("#extractionTableBody .editable-row").remove();
}



    /* DELETING */
// ============================================================== //
function confirmDeleteExtraction(productId) {
    // Display a confirmation dialog to the user
    if (confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
        // Proceed with deletion if the user confirms
        deleteExtraction(productId);
    }
}

function deleteExtraction(productId) {
    // Send the DELETE request to the server
    fetch(`api/extractions/${productId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            response_modal(data.message || "Apportion item deleted successfully.");
            // Remove the deleted row from the table or refresh the table
            document.querySelector(`tr[data-item-id="${productId}"]`).remove();
        } else {
            response_modal(data.error || "An error occurred while deleting the item.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Failed to delete the apportion item due to a network error.");
    });
}