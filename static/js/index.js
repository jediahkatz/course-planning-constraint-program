function add_requested_course() {
    // Number of inputs to create
    var college = $("#select-couse").value;
    // this clears the select field and selects the default value
    $("#select-college")[0].selectize.clear();

    alertBox = $("#course-alert-box");
    alertLine = $("#course-alert");
    if (college == "") {
        alertBox.style.display = "block";
        alertLine.textContent = "Please enter colleges from the available list";
        return;
    }
    if (collegeOpeidList.includes(opeid)) {
        alertBox.style.display = "block";
        alertLine.textContent = "This college is already in the list";
        return;
    }
    alertBox.style.display = "none";
    alertLine.textContent = "";
    collegeNameList.push(college);
    collegeOpeidList.push(opeid);
    collegeCount++;
    // Container <div> where dynamic content will be placed
    var container = document.getElementById("collegeListContainer");
    container.appendChild(
        document.createTextNode(collegeCount + ". " + college)
    );
    container.appendChild(document.createElement("br"));
    container.scrollIntoView({ behavior: "smooth", block: "start" });
}
