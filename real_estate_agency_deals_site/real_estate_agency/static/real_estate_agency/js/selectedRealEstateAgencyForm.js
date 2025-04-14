function selectedRealEstateAgencyForm() {
    const select = document.getElementById('id_type');
    console.log(select)
    const arraySelect = [
        document.getElementById('apartment'),
        document.getElementById('house'),
        document.getElementById('plot')
    ];

    for (const div of arraySelect) {
        div.style.display = 'none';
    }

    let selectedValue = select?.value;

    if (selectedValue && arraySelect[selectedValue]) {
        arraySelect[selectedValue].style.display = 'block';
    }
}

function selectedAddressRealEstateForm() {
    const checkbox = document.getElementById('id_have_address');
    const address = document.getElementById('address_real_estate');

    address.style.display = 'none';

    let isChecked = checkbox?.checked;

    if (isChecked && address) {
        address.style.display = 'block';
    }
}

document.getElementById('id_type').addEventListener('change', selectedRealEstateAgencyForm);
document.getElementById('id_have_address').addEventListener('change', selectedAddressRealEstateForm);

selectedAddressRealEstateForm();
selectedRealEstateAgencyForm();
