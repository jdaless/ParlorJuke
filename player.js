var app = angular.module('player', ['ngMaterial']);

app.controller('Queue', function($scope, $rootScope, $http, $interval) {
	$queueRefreshed = false;
	$scope.progress = 0;
	function refreshQueue(){
		$http.get("api/player").then(function(response) {
	        $fullQueue = response.data;
				$scope.nowPlaying = $fullQueue[0];
				$scope.queue = $fullQueue[1];
				$scope.started = $fullQueue[2];
				console.log($fullQueue)
				$queueRefreshed = true;
	    });
	}

    $rootScope.$on("RefreshQueue", function(){
       refreshQueue();
    });

	refreshQueue();
	$interval(function() {
		$time = new Date().getTime();
		if($queueRefreshed && $scope.nowPlaying){
			$scope.progress = ($time - ($scope.started*1000)) / ($scope.nowPlaying.length*10);
		}
		else{
			$scope.progress = 101;
		}
		if($scope.progress>100  && $scope.nowPlaying && $scope.nowPlaying.title){
			refreshQueue();
		}
	}, 100, 0, true);
});

app.directive('fileModel', ['$parse', function ($parse) {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			var model = $parse(attrs.fileModel);
			var modelSetter = model.assign;

			element.bind('change', function(){
				scope.$apply(function(){
					modelSetter(scope, element[0].files[0]);
				});
			});
		}
	};
}]);

app.controller('AddMenu', function($scope, $rootScope, $http, $mdSidenav){
	$scope.openSideNav = function (){
	    $mdSidenav('add').open();
	};
	$scope.browseFiles = function(){
		$mdSidenav('add').close();
		$mdSidenav('fromLocal').open();
		$http.get("api/library.php").then(function(response) {
	        $response = response.data;
			$scope.library = $response;
	    });
	};
	$scope.openUpload = function(){
		$mdSidenav('add').close();
		$mdSidenav('upload').open();
	};
	$scope.currentSearch = 'queue_music';
	$scope.openQueryMenu= function($mdOpenMenu, ev) {
      originatorEv = ev;
      $mdOpenMenu(ev);
    };
	$scope.addSong = function(song){
		id = $scope.library.indexOf(song);
		$http.get("api/library.php?id=" + id).then(function(response) {
			$rootScope.$emit("RefreshQueue", {});
			$mdSidenav('fromLocal').close();
	    });
	};
	$scope.uploadFile = function(){
		var ErrorEnum = {Filetype: 1, Size: 2, Exists: 4, SaveFail: 8}
		var file = $scope.fileToUpload;
		var fd = new FormData();
		fd.append("file", file);
		$scope.uploading = true;
        $http.post("api/upload.php", fd, {
    		transformRequest: angular.identity,
    		headers: {'Content-Type': undefined}
		}).then(function(response){
			$scope.uploading = false;
			if(response.data == 0){
				$scope.message = "Upload Successful";
			}
			else{
				$scope.message = "Upload Failed: \n";
			}
			if(response.data & ErrorEnum.Filetype){
				$scope.message = $scope.message + "Please use .mp3 format\n";
			}
			if(response.data & ErrorEnum.Size){
				$scope.message = $scope.message + "File too large\n";
			}
			if(response.data & ErrorEnum.Exists){
				$scope.message = $scope.message + "That file is already in the library\n";
			}
			if(response.data & ErrorEnum.SaveFail){
				$scope.message = $scope.message + "Unknown error, file failed to save\n";
			}
		});
	};
});
