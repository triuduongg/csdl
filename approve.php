<?php
include './connect.php';
include './uploads/logfunctions/LoginLog.php';
session_start();
if(isset($_GET['a'])){
    $v = $_GET['a'];
    $query = mysqli_query($c, "select * from notification where notID = '$v'");
    $array = mysqli_fetch_assoc($query);
    mysqli_query($c, "INSERT INTO `user` (`userID`, `fullname`, `email`, `password`, `title`, `role`, `tel`, `status`) VALUES (NULL, '$array[fullname]', '$array[email]', '$array[password]', '$array[title]', '0', '$array[contact]', '0')");
    mysqli_query($c, "delete from notification where notID = '$v'");
    $path = './uploads/logs/'.$array['email'].'.txt';
    $handle = fopen($path,'w' );
    $content = '';
    fwrite($handle, $content);
    fclose($handle);
    LoginLog($_SESSION['id'], 'was used to approve account creation for user under the email of '.$array['email']);
}
if(isset($_GET['r'])){
    $v = $_GET['r'];
    mysqli_query($c, "delete from notification where notID = '$v'");
    LoginLog($_SESSION['id'], 'was used to revoke account creation request for notification ID '.$v);
}

header('Location: admindashboard.php');
