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