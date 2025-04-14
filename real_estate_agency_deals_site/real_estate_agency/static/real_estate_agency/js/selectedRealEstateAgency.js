function selectedRealEstateAgency() {
    const radios = document.getElementsByName('type_real_estate');
    const divs = {
        apartment_only: document.getElementById('apartment'),
        house_only: document.getElementById('house'),
        plot_only: document.getElementById('plot')
    };

    for (const div of Object.values(divs)) {
        div.style.display = 'none';
    }

    let selectedValue = Array.from(radios).find(radio => radio.checked)?.value;

    if (selectedValue && divs[selectedValue]) {
        divs[selectedValue].style.display = 'block';
    }
}

function selectedDeal() {
    const radios = document.getElementsByName('type_deal');
    const divs = {
        deal_rent_only: document.getElementById('rent'),
        deal_construction_only: document.getElementById('construction')
    };

    for (const div of Object.values(divs)) {
        div.style.display = 'none';
    }

    let selectedValue = Array.from(radios).find(radio => radio.checked)?.value;

    if (selectedValue && divs[selectedValue]) {
        divs[selectedValue].style.display = 'block';
    }
}

function selectedAddressRealEstate() {
    const radios = document.getElementsByName('address_real_estate');
    const address = document.getElementById('address');

    address.style.display = 'none';

    let selectedValue = Array.from(radios).find(radio => radio.checked)?.value;

    if (selectedValue && selectedValue === 'address_real_estate_exist') {
        address.style.display = 'block';
    }
}
