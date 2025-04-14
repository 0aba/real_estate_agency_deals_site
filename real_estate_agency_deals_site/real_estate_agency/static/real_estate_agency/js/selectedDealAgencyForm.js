function selectedDealAgencyForm() {
    const select = document.getElementById('id_type');
    const arraySelect = [
        document.getElementById('rent'),
        document.getElementById('construction')
    ];

    for (const div of arraySelect) {
        div.style.display = 'none';
    }

    let selectedValue = select?.value - 1;

    if (arraySelect[selectedValue]) {
        arraySelect[selectedValue].style.display = 'block';
    }
}


document.getElementById('id_type').addEventListener('change', selectedDealAgencyForm);

selectedDealAgencyForm();
