let counter = 3;

let addGroupButton = document.getElementById("add-group-button");
let groupContainer = document.getElementById("discussion-group-container");

addGroupButton.addEventListener("click", function() {

    counter += 1;

    groupContainer.innerHTML += `<div style="padding: 0px 10px 2px 10px">
    <div style="width:100%; height:100px; border:1px solid; border-radius:25px; padding: 4px 0 10px 10px">
        <p>Disussion Group ${counter}</p>
        <hr />
        <p>This is discussion ${counter}'s description. This will include general information about the group and its members.</p>
    </div>
</div>

<hr />`;

});