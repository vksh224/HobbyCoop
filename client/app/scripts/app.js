'use strict';

/**
 * @ngdoc overview
 * @name h4hApp
 * @description
 * # h4hApp
 *
 * Main module of the application.
 */
var myApp = angular
  .module('h4hApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ngAutocomplete',
    'angularModalService',
    'ngTagsInput'
  ]);

myApp.config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        controllerAs: 'main'
      })
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl',
        controllerAs: 'about'
      })
      .when('/createAccount', {
        templateUrl: 'views/createAccount.html',
        controller: 'CreateAccountCtrl',
        controllerAs: 'account'
      })
      .when('/myAccount',{
        templateUrl: 'views/myAccount.html',
        controller: 'MyAccountCtrl',
        controllerAs: 'myAccount'
      })
      .when('/rentAnItem',{
        templateUrl: 'views/rentAnItem.html',
        controller: 'RentAnItemCtrl',
        controllerAs: 'rentAnItem'
      })
      .when('/itemDetail', {
        templateUrl: 'views/itemDetail.html',
        controller: 'ItemDetailCtrl'
      })
      .when('/searchResults',{
        templateUrl: 'views/searchResults.html',
        controller: 'SearchResultsCtrl',
        controllersAs: 'searchResults'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
