function selectedDealAgencyForm() {
    const select = document.getElementById('id_type_deal');
    const arraySelect = [
        document.getElementById('rent'),
        document.getElementById('construction')
    ];

    for (const div of arraySelect) {
        div.style.display = 'none';
    }

    let selectedValue = select?.value - 1;
    console.log(select?.value)

    if (arraySelect[selectedValue]) {
        arraySelect[selectedValue].style.display = 'block';
    }
}


document.getElementById('id_type_deal')?.addEventListener('change', selectedDealAgencyForm);

selectedDealAgencyForm();
