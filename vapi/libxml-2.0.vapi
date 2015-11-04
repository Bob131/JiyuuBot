/* libxml2.vala
 *
 * Copyright (C) 2006-2008  Jürg Billeter, Raffaele Sandrini, Michael Lawrence
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.

 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.

 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
 *
 * Author:
 * 	Jürg Billeter <j@bitron.ch>
 *	Raffaele Sandrini <rasa@gmx.ch>
 *	Michael Lawrence <lawremi@iastate.edu>
 *	Ondřej Jirman <megous@megous.com>
 */

namespace Html {
	[Compact]
	[CCode (cname = "htmlEntityDesc", cheader_filename = "libxml/HTMLparser.h")]
	public class EntityDesc
	{
		public uint value;
		public weak string name;
		public weak string desc;

		[CCode (cname = "htmlEntityLookup")]
		public static EntityDesc* lookup ([CCode (type = "xmlChar*")] string name);

		[CCode (cname = "htmlEntityValueLookup")]
		public static EntityDesc* value_lookup (uint value);
	}
}
