"""Plugin names and new errors; legacy codes remain stable."""
KEYWORD = "UsdAecoValidators"
IDENTITY_CHECKER = 'usdAecoValidators:IdentityChecker'
SPATIAL_GRAMMAR_CHECKER = 'usdAecoValidators:SpatialGrammarChecker'
CLASSIFICATION_CHECKER = 'usdAecoValidators:ClassificationChecker'
PORT_CONNECTIVITY_CHECKER = 'usdAecoValidators:PortConnectivityChecker'
GROUP_CHECKER = 'usdAecoValidators:GroupChecker'
DERIVED_GEOMETRY_CHECKER = 'usdAecoValidators:DerivedGeometryChecker'
DERIVED_EXACT_ON_MESH_CHECKER = 'usdAecoValidators:DerivedExactOnMeshChecker'
EXACT_WITHOUT_TOLERANCE_CHECKER = 'usdAecoValidators:ExactWithoutToleranceChecker'
DERIVED_EXACT_ON_MESH = "DerivedExactOnMesh"
EXACT_WITHOUT_TOLERANCE = "ExactWithoutTolerance"
ERROR_NAMES = (DERIVED_EXACT_ON_MESH, EXACT_WITHOUT_TOLERANCE)
LEGACY_ERROR_NAMES = ('asymmetricPortLink', 'badSpatialNesting', 'danglingMember', 'danglingPortLink', 'derivedGeometryOrphan', 'derivedGeometryPurpose', 'derivedGeometryRole', 'duplicateId', 'elevationDrift', 'emptyClassificationCode', 'facilityInFacility', 'incompatibleFlow', 'levelWithoutElevation', 'malformedId', 'mediumMismatch', 'missingId', 'portIsElement', 'proxyClassified', 'servesTargetsNonSpatial', 'spatialInsideElement', 'spatialIsElement', 'unanchoredSpatial', 'unclassifiedElement', 'unregisteredClassificationSystem', 'zoneAuthorsServes')
