const buttons = document.querySelectorAll(".btn");
const boxes = document.querySelectorAll(".box");
const searchbox = document.querySelector("#search");


function filterItems() {
    
    const filterValue = document.querySelector(".btn-clicked").dataset.filter;
    const searchText = searchbox.value.toLowerCase().trim();

    boxes.forEach(box => {
        const itemType = box.dataset.item.toLowerCase();       
        const matchesFilter = filterValue === 'all' || itemType === filterValue;
        const matchesSearch = itemType.includes(searchText);   
        if (matchesFilter && matchesSearch) {
            box.style.display = "block";
        } else {
            box.style.display = "none";
        }
    });
}
buttons.forEach(button => {
    button.addEventListener("click", (e) => {
        
        document.querySelector(".btn-clicked").classList.remove("btn-clicked");
        button.classList.add("btn-clicked");
        filterItems(); 
    });
});


searchbox.addEventListener("keyup", filterItems);
