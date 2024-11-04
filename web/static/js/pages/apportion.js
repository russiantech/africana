    document.addEventListener('DOMContentLoaded', function () {
        // Load main products on page load
        fetchMainProducts();
        // Add event listeners for each tab to load data when clicked
        document.querySelector('#pills-main-tab').addEventListener('click', fetchMainProducts);
    });
    
    function fetchMainProducts(){
        fetch('api/apportions')
            .then(response => response.json())
            .then(data => {
                //console.log(data.data.items)
                populateTable(data.data.items, 'mainTableBody');
            })
            .catch(error => console.error('Error fetching main products:', error));
    }
    
    function populateTable(items, tableId) {
        const tableBody = document.querySelector(`#${tableId}`);
        tableBody.innerHTML = ''; // Clear existing rows
        
        // Check if items is defined and has the expected structure
        if (items.length > 0) {
            //console.log(items)
            items.forEach(item => {
                let row = `
                    <tr data-item-id="${item.id}">
                        <td>${item.id}</td>
                        <td>${item.dept === 'k' ? 'Kitchen' : item.dept === 'c' ? 'Cocktail' : 'Bar'}</td>
                        <td>${item.product_title}</td>
                        <td>${item.main_qty}</td>
                        <td>${item.initial_apportioning}</td>
                        <td>${item.apportioned_qty}</td>
                        <td>${item.extracted_qty}</td>
                        <td>N${item.cost_price}</td>
                        <td>${item.created_at}</td>
                        <td>
                            <div class="d-flex align-items-center list-action">
                                <button class="badge bg-success mr-2 border-none" onclick="makeRowEditable(${item.id})"><i class="ri-pencil-line mr-0"></i></a>
                                <button class="badge bg-warning mr-2 border-none" onclick="confirmDeleteItem(${item.id})"><i class="ri-delete-bin-line mr-0"></i></a>
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
    document.querySelector('.new-product-row-btn').addEventListener('click', create_editable_row);
});

function create_editable_row() {
    let tableBody = document.querySelector("#mainTableBody");

    // Check if there's already an editable row and prevent adding multiple
    if (document.querySelector("#mainTableBody .editable-row") ) {
        response_modal('You already have a row being edited.');
        return;
    }

    // Create a new row with input fields
    let newRow = document.createElement("tr");
    newRow.classList.add("editable-row");
    newRow.innerHTML = `
    <tr>
        <td>-</td>
        <td>
            <select class="form-control" id="apportion_dept">
                <option value="k">Kitchen</option>
                <option value="c">Cocktail</option>
                <option value="b">Bar</option>
            </select>
        </td>
        <td><input type="text" class="form-control" id="product_title" placeholder="Product Title"></td>
        <td><input type="number" class="form-control" id="main_qty" value="0" placeholder="Main Quantity"></td>
        <td><input type="number" class="form-control" id="initial_apportioning" value="0" placeholder="initial Apportioning"></td>
        <td>-</td>
        <td>-</td>
        <td><input type="number" class="form-control" id="cost_price" value="0" placeholder="Cost"></td>
        <td>-</td>
        <td>
            <button class="btn btn-success" onclick="submitNewProduct()"><i class="las la-plus mr-0"></i></button>
            <button class="btn btn-secondary" onclick="cancelNewProduct()"><i class="ri-close-line"></i></button>
        </td>
    </tr>
    `;

    // Insert the new row at the top of the table body
    tableBody.insertBefore(newRow, tableBody.firstChild);
}

function submitNewProduct() {
    // Get the new product details from the inputs
    let apportionDept = document.getElementById("apportion_dept").value;
    let productTitle = document.getElementById("product_title").value;
    let mainQty = document.getElementById("main_qty").value;
    let apportionedQty = document.getElementById("initial_apportioning").value;
    let costPrice = document.getElementById("cost_price").value;

    // Validate inputs
    if (!productTitle || !mainQty || !apportionedQty) {
        response_modal('Please fill in all the fields.');
        return;
    }

    let data = {
        apportion_dept: apportionDept,
        product_title: productTitle,
        main_qty: mainQty,
        initial_apportioning: apportionedQty,
        cost_price: costPrice
    };

    // Call the backend API to save the new product
    fetch('/api/apportions', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // Prepare the new row with saved data
            let tableBody = document.querySelector("#mainTableBody");
            let newRow = document.createElement("tr");
            newRow.innerHTML = `
            <tr data-item-id="${result.data.id}">
                <td>${result.data.id}</td>
                <td>${result.data.apportion_dept === 'k' ? 'Kitchen' : result.data.apportion_dept === 'c' ? 'Cocktail' : 'Bar'}</td>
                <td>${result.data.product_title || 'N/A'}</td>
                <td>${result.data.main_qty || 0}</td>
                <td>${result.data.initial_apportioning || 0}</td>
                <td>-</td>
                <td>-</td>
                <td>N${result.data.cost_price || 0}</td>
                <td>${result.data.created_at || 'Not available'}</td>
                <td>
                    <div class="d-flex align-items-center list-action"> 
                        <button class="badge bg-success mr-2 border-none" onclick="makeRowEditable(${result.data.id})><i class="ri-pencil-line mr-0"></i></button>
                        <button class="badge bg-warning mr-2 border-none" onclick="confirmDeleteItem(${result.data.id})"><i class="ri-delete-bin-line mr-0"></i></button>
                    </div>
                </td>
            </tr>
            `;

            tableBody.insertBefore(newRow, tableBody.firstChild);

            // Remove the editable row
            document.querySelector("#mainTableBody .editable-row").remove();

            // Show success message
            response_modal(result.message);

        } else {
            response_modal(`Error adding product - ${result.error}`);
        }
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        response_modal("A network error occurred: " + error.message);
    });
}

function cancelNewProduct() {
    // Remove the input row without saving
    document.querySelector("#mainTableBody .editable-row").remove();
}

    /* EDITING */
// ============================================================== //

function makeRowEditable(productId) {
    // Check if there's already an editable row
    if (document.querySelector(".editable-row")) {
        response_modal("You already have a row being edited.");
        return;
    }

    let row = document.querySelector(`tr[data-item-id="${productId}"]`);
    row.classList.add("editable-row");

    // Get current values from the row's cells
    let dept = row.children[1].textContent.trim();
    let productTitle = row.children[2].textContent.trim();
    let mainQty = row.children[3].textContent.trim();
    let initialApportioning = row.children[4].textContent.trim();
    let costPrice = row.children[7].textContent.trim();
        // Convert costPrice to a numeric value, removing non-numeric characters
    costPrice = parseFloat(costPrice.replace(/[^\d.]/g, '')) || 0;
    
    // Replace row with editable input fields
    row.innerHTML = `
        <td>${productId}</td>
        <td>
            <select class="form-control" id="edit_apportion_dept">
                <option value="k" ${dept === 'Kitchen' ? 'selected' : ''}>Kitchen</option>
                <option value="c" ${dept === 'Cocktail' ? 'selected' : ''}>Cocktail</option>
                <option value="b" ${dept === 'Bar' ? 'selected' : ''}>Bar</option>
            </select>
        </td>
        <td><input type="text" class="form-control" id="edit_product_title" value="${productTitle}"></td>
        <td><input type="number" class="form-control" id="edit_main_qty" value="${mainQty}"></td>
        <td><input type="number" class="form-control" id="edit_initial_apportioning" value="${initialApportioning}"></td>
        <td><input type="number" class="form-control" id="edit_apportioned_qty" value="${initialApportioning}"></td>
        <td>-</td>
        <td><input type="number" class="form-control" id="edit_cost_price" value="${costPrice}"></td>
        <td>-</td>
        <td>
            <button class="btn btn-success" onclick="submitUpdatedItem(${productId})"><i class="las la-save mr-0"></i></button>
            <button class="btn btn-secondary" onclick="cancelEdit()"><i class="ri-close-line"></i></button>
        </td>
    `;
}

function submitUpdatedItem(productId) {
    let dept = document.getElementById("edit_apportion_dept").value;
    let productTitle = document.getElementById("edit_product_title").value;
    let mainQty = parseFloat(document.getElementById("edit_main_qty").value) || 0;
    let initialApportioning = parseFloat(document.getElementById("edit_initial_apportioning").value) || 0;
    let apportionedQty = parseFloat(document.getElementById("edit_apportioned_qty").value) || 0;
    let costPrice = parseFloat(document.getElementById("edit_cost_price").value) || 0;

    let data = {
        dept: dept,
        product_title: productTitle,
        main_qty: mainQty,
        initial_apportioning: initialApportioning,
        apportioned_qty: apportionedQty,
        cost_price: costPrice,
    };

    fetch(`api/apportions/${productId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            response_modal(result.message);
            //location.reload(); // Reload table or dynamically update the row
        } else {
            response_modal(`Error: ${result.error}`);
        }
    })
    .catch(error => response_modal(`Error: ${error}`));
}

function cancelEdit() {
    document.querySelector("#mainTableBody .editable-row").remove();
}


    /* DELETING */
// ============================================================== //
function confirmDeleteItem(productId) {
    // Display a confirmation dialog to the user
    if (confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
        // Proceed with deletion if the user confirms
        deleteItem(productId);
    }
}

function deleteItem(productId) {
    // Send the DELETE request to the server
    fetch(`api/apportions/${productId}`, {
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