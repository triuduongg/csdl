<?php
include './connect.php';
if(isset($_POST['submit'])){
    $fullname = $_POST['fullname'];
    $email = $_POST['email'];
    $contact = $_POST['contact'];
    $password = $_POST['password'];
    $position = $_POST['position'];

    mysqli_query($c, "INSERT INTO `notification` (`notID`, `fullname`, `title`, `email`, `contact`, `password`) VALUES (NULL, '$fullname', '$position', '$email', '$contact', '$password')");


}
header('Location: adminlogin.html');