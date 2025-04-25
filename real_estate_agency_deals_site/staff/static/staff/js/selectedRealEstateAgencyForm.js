function selectedRealEstateAgency() {
    const select = document.getElementById('id_type_real_estate');
    const arraySelect = [
        document.getElementById('apartment'),
        document.getElementById('house'),
        document.getElementById('plot')
    ];

    for (const div of arraySelect) {
        div.style.display = 'none';
    }

    let selectedValue = select?.value;

    if (arraySelect[selectedValue]) {
        arraySelect[selectedValue].style.display = 'block';
    }
}

document.getElementById('id_type_real_estate')?.addEventListener('change', selectedRealEstateAgency);

selectedRealEstateAgency();

