# 7 · Worked core examples

The six [example stages](../usdAeco/examples/) cover a small building,
early design, recursive containment, renovation, a road and a service campus.
The minimal alias selects early design. All use core semantics and ordinary
USD representations; no construction driver API is required.

The two examples below are complete stages. Save each block under its stated
filename in one directory, then open `pipe.usda` or `wall.usda`. The checks
extract these exact blocks, compose both roots and run the core validators.
Geometry opinions live in the stronger derived layer; muting it preserves
referent identity, classification and connectivity.

## 7.1 A pipe run

Two classified segments connect at coincident end ports. The cylinders
are a descriptive representation with assumed dimensions.

### `pipe.usda`

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
    fallbackPrimTypes = {
        token[] AecoFacility = ["Xform"]
        token[] AecoPort = ["Xform"]
    }
    subLayers = [@pipe.derived.usda@, @pipe.semantics.usda@]
)
```

### `pipe.semantics.usda`

```usda
#usda 1.0
def Xform "World"
{
    def AecoFacility "Building"
    {
        string aeco:id = "00000000-0000-4000-8000-000000000001"
        def Xform "First" (
            prepend apiSchemas = ["AecoElementAPI", "AecoClassificationAPI:ifc"]
        )
        {
            string aeco:id = "00000000-0000-4000-8000-000000000002"
            string aeco:class:ifc:code = "IfcPipeSegment.RIGIDSEGMENT"
            uniform token aeco:phase = "proposed"
            def AecoPort "End"
            {
                string aeco:id = "00000000-0000-4000-8000-000000000004"
                uniform token aeco:medium = "pipe"
                uniform token aeco:flowDirection = "bidirectional"
                rel aeco:connectedPorts = </World/Building/Second/End>
                double3 xformOp:translate = (2, 0, 0)
                uniform token[] xformOpOrder = ["xformOp:translate"]
            }
        }
        def Xform "Second" (
            prepend apiSchemas = ["AecoElementAPI", "AecoClassificationAPI:ifc"]
        )
        {
            string aeco:id = "00000000-0000-4000-8000-000000000003"
            string aeco:class:ifc:code = "IfcPipeSegment.RIGIDSEGMENT"
            uniform token aeco:phase = "proposed"
            def AecoPort "End"
            {
                string aeco:id = "00000000-0000-4000-8000-000000000005"
                uniform token aeco:medium = "pipe"
                uniform token aeco:flowDirection = "bidirectional"
                rel aeco:connectedPorts = </World/Building/First/End>
                double3 xformOp:translate = (2, 0, 0)
                uniform token[] xformOpOrder = ["xformOp:translate"]
            }
        }
    }
}
```

### `pipe.derived.usda`

```usda
#usda 1.0
over "World"
{
    over "Building"
    {
        over "First"
        {
            def Cylinder "Body" (
                prepend apiSchemas = ["AecoDerivedGeometryAPI"]
            )
            {
                string aeco:derived:source = "00000000-0000-4000-8000-000000000002"
                uniform token aeco:derived:role = "body"
                uniform token aeco:derived:approx = "defaultDims"
                string aeco:derived:stamp = "core example 0.9.1"
                uniform token purpose = "render"
                uniform token axis = "X"
                double height = 2
                double radius = 0.05
                double3 xformOp:translate = (1, 0, 0)
                uniform token[] xformOpOrder = ["xformOp:translate"]
            }
        }
        over "Second"
        {
            def Cylinder "Body" (
                prepend apiSchemas = ["AecoDerivedGeometryAPI"]
            )
            {
                string aeco:derived:source = "00000000-0000-4000-8000-000000000003"
                uniform token aeco:derived:role = "body"
                uniform token aeco:derived:approx = "defaultDims"
                string aeco:derived:stamp = "core example 0.9.1"
                uniform token purpose = "render"
                uniform token axis = "X"
                double height = 2
                double radius = 0.05
                double3 xformOp:translate = (3, 0, 0)
                uniform token[] xformOpOrder = ["xformOp:translate"]
            }
        }
    }
}
```

## 7.2 A wall corner

Two classified elements form a right-angle corner. Their ports describe a
physical assembly connection; core specifies no trimming or join algorithm.
The cubes have assumed dimensions, declared by the representation mark.

### `wall.usda`

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
    fallbackPrimTypes = {
        token[] AecoFacility = ["Xform"]
        token[] AecoPort = ["Xform"]
    }
    subLayers = [@wall.derived.usda@, @wall.semantics.usda@]
)
```

### `wall.semantics.usda`

```usda
#usda 1.0
def Xform "World"
{
    def AecoFacility "Building"
    {
        string aeco:id = "00000000-0000-4000-8000-000000000001"
        def Xform "First" (
            prepend apiSchemas = ["AecoElementAPI", "AecoClassificationAPI:ifc"]
        )
        {
            string aeco:id = "00000000-0000-4000-8000-000000000002"
            string aeco:class:ifc:code = "IfcWall.PARTITIONING"
            uniform token aeco:phase = "proposed"
            def AecoPort "End"
            {
                string aeco:id = "00000000-0000-4000-8000-000000000004"
                uniform token aeco:medium = "other"
                uniform token aeco:flowDirection = "bidirectional"
                rel aeco:connectedPorts = </World/Building/Second/End>
                double3 xformOp:translate = (4, 0, 0)
                uniform token[] xformOpOrder = ["xformOp:translate"]
            }
        }
        def Xform "Second" (
            prepend apiSchemas = ["AecoElementAPI", "AecoClassificationAPI:ifc"]
        )
        {
            string aeco:id = "00000000-0000-4000-8000-000000000003"
            string aeco:class:ifc:code = "IfcWall.PARTITIONING"
            uniform token aeco:phase = "proposed"
            def AecoPort "End"
            {
                string aeco:id = "00000000-0000-4000-8000-000000000005"
                uniform token aeco:medium = "other"
                uniform token aeco:flowDirection = "bidirectional"
                rel aeco:connectedPorts = </World/Building/First/End>
                double3 xformOp:translate = (4, 0, 0)
                uniform token[] xformOpOrder = ["xformOp:translate"]
            }
        }
    }
}
```

### `wall.derived.usda`

```usda
#usda 1.0
over "World"
{
    over "Building"
    {
        over "First"
        {
            def Cube "Body" (
                prepend apiSchemas = ["AecoDerivedGeometryAPI"]
            )
            {
                string aeco:derived:source = "00000000-0000-4000-8000-000000000002"
                uniform token aeco:derived:role = "body"
                uniform token aeco:derived:approx = "defaultDims"
                string aeco:derived:stamp = "core example 0.9.1"
                uniform token purpose = "render"
                double size = 2
                double3 xformOp:translate = (2, 0, 1.5)
                float3 xformOp:scale = (2, 0.1, 1.5)
                uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
            }
        }
        over "Second"
        {
            def Cube "Body" (
                prepend apiSchemas = ["AecoDerivedGeometryAPI"]
            )
            {
                string aeco:derived:source = "00000000-0000-4000-8000-000000000003"
                uniform token aeco:derived:role = "body"
                uniform token aeco:derived:approx = "defaultDims"
                string aeco:derived:stamp = "core example 0.9.1"
                uniform token purpose = "render"
                double size = 2
                double3 xformOp:translate = (4, 1.5, 1.5)
                float3 xformOp:scale = (0.1, 1.5, 1.5)
                uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
            }
        }
    }
}
```

## 7.3 Read and validate

With the schema and validator paths configured as in the root README:

```sh
python tools/aeco_core.py check pipe.usda
python tools/aeco_core.py check wall.usda
```

Both stages have two classified elements, two connected ports and two marked
body gprims. All typed core prims have stock fallbacks. The same files open
without plugins, retaining transforms and authored data. The port network
supports connectivity queries; the mark identifies the source of each body.
Dimensions are illustrative, so neither example claims reconstruction accuracy.
