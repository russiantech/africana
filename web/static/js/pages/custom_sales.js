
document.addEventListener('DOMContentLoaded', () => {
    // Fetch and populate dropdowns when the modal opens
    // $('#record-complimentary-sales').on('show.bs.modal', function () {
    //     fetchItems();
    //     fetchExtractions();
    // });

    // function fetchItems(dept=null) {
    window.fetchItems = function(dept) {
        fetch(`api/items?per_page=10000&dept=${dept}`)
            .then(response => response.json())
            .then(data => {
                // Assuming data.data.items contains the relevant items
                populateSelect(data.data.items, 'item_id');
            })
            .catch(error => console.error('Error fetching items:', error));
    }

    // function fetchExtractions(dept=null) {
    window.fetchExtractions = function(dept) {
        fetch(`api/extractions?per_page=10000&dept=${dept}`)
            .then(response => response.json())
            .then(data => {
                // Assuming data.data.items contains the relevant items
                populateSelect(data.data.items, 'extracted_id');
            })
            .catch(error => console.error('Error fetching extractions:', error));
    }

    function populateSelect(items, selectFieldId) {
        const dropdown = document.getElementById(selectFieldId);
        dropdown.innerHTML = ''; // Clear existing options
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.className = 'text-warning disabled';
        defaultOption.value = '';
        defaultOption.textContent = selectFieldId === 'item_id' ? 'Select Stock' : 'Select Apportioned/Extracted';
        dropdown.appendChild(defaultOption);
    
        // Check if items is defined and has the expected structure
        if (Array.isArray(items) && items.length > 0) {
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item.title || item.name || item.extracted_title || 'Unknown Item';
                option.setAttribute('data-price', item.price || '0'); // If you have a price attribute
                option.setAttribute('data-id', item.id); // Additional attributes if necessary
                dropdown.appendChild(option);
            });
        } else {
            dropdown.innerHTML = '<option>No items found.</option>';
        }
    
        // Refresh the select picker to reflect changes, if it exists
        if (typeof $ !== 'undefined' && $(dropdown).hasClass('selectpicker')) {
            $(dropdown).selectpicker('refresh');
        }
    }
    
    // form submission handler for new sales.
    document.querySelector('.btn-outline-primary.submit').addEventListener('click', function (event) {
        event.preventDefault();  // Prevent default form submission

        const item_id = document.getElementById('item_id').value;
        const extracted_id = document.getElementById('extracted_id').value;
        const title = document.querySelector('input[name="title"]').value;
        const qty = document.querySelector('input[name="quantity_used"]').value;
        const price = document.querySelector('input[name="price"]').value;
        const dept = document.querySelector('select[name="insert-dept"]').value;

        const payload = { item_id, extracted_id, title, qty, price, dept };
        console.log(payload)
        fetch('api/sales', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.success) {
                response_modal(data.message);
                $('#record-complimentary-sales').modal('hide');
                //location.reload();  // Optional, reload to show updated data
            } else {
                response_modal(data.error || 'Failed to record sale');
            }
        })
        .catch(error => console.error('Error submitting form:', error));
    });
});

/* PDF REPORT GENERATION */
    // Function to generate PDF of the entire page
    const generatePDF = () => {
        // Select the download button and set loading state
        const downloadButton = document.getElementById('download_report_pdf');
        downloadButton.innerHTML = '<i class="fa fa-circle-notch fa-spin fa-1x fa-fw"></i>';

        // Capture the entire page content as PDF
        html2pdf()
            .set({
                filename: 'reportings.pdf',
                image: { type: 'jpeg', quality: 0.9 },
                enableLinks: true,
                jsPDF: { format: 'A4', orientation: 'landscape' },
                margin: [4, 10, 0, 10],
                autoPaging: 'text',
            })
            //.from(document.body)  // Capture entire body
            .from(document.querySelector('.container-sales'))  // Capture entire body
            .save()
            .then(() => {
                // Restore button to original state
                downloadButton.innerHTML = 'Download Report Page(PDF)';
            })
            .catch((error) => {
                console.error('PDF generation failed:', error);
                downloadButton.innerHTML = 'Download Page As PDF(Report)';  // Reset button text if error
            });
    };

    // Attach the function to be triggered by the download button click after the page fully loads
    window.addEventListener('load', () => {
        const downloadButton = document.getElementById('download_report_pdf');
        if (downloadButton) {
            downloadButton.addEventListener('click', generatePDF);
        }
    });